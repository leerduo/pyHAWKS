# -*- coding: utf-8 -*-
# par2norm.py

# v0.2
# Christian Hill, 3/8/12
#
# Methods to parse a .par file into normalized .states and .trans files
import os
import sys
import time

from pyHAWKS_config import SETTINGS_PATH, HITRAN1986_SOURCEID
from hitran_transition import HITRANTransition
from xn_utils import vprint
from fmt_xn import trans_fields
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranlbl.models import State

def parse_par(args, molecule, isos, d_refs):
    """
    Parse the input .par file, args.par_file, into normalized .states and
    .trans files, checking for the existence of the relevant sources and
    not outputing duplicates. All transitions encountered are written to
    the .trans file, even if they're already in the database - duplicate-
    handling is done upon staging the upload.
    NB the input .par file must be in order of increasing wavenumber
    (an error is raised if this is found not to be the case).

    """

    # get all of the states for this molecule currently in the database
    # as their string representations - these are the keys to the db_stateIDs
    # dictionary, with the corresponding database State ids as their values
    db_stateIDs = {}
    for state in State.objects.filter(iso__in=isos):
        db_stateIDs[state.str_rep()] = state.id
                                
    vprint('%d existing states for %s read in from database'\
                % (len(db_stateIDs), molecule.ordinary_formula))

    vprint('Creating .trans and .states files...')
    vprint('%s\n-> %s\n   %s'\
            % (args.par_file, args.trans_file, args.states_file))

    if not args.overwrite:
        # the .trans and .states files should not already exist
        for filename in (args.trans_file, args.states_file):
            if os.path.exists(filename):
                vprint('File exists:\n%s\nAborting.' % filename, 5)
                sys.exit(1)

    # read the lines and rstrip them of the EOL characters. We don't lstrip
    # because we keep the space in front of molec_ids 1-9
    vprint('reading .par lines from %s ...' % args.par_file)
    lines = [x.rstrip() for x in open(args.par_file, 'r').readlines()]
    ntrans = len(lines)
    vprint(ntrans, 'lines read in')

    # find out the state ID at which we can start adding states
    try:
        first_stateID = State.objects.all().order_by('-id')[0].id + 1
    except IndexError:
        # no states in the database yet, so let's start at 1
        first_stateID = 1
    vprint('new states will be added with ids starting at %d' % first_stateID)

    fo_s = open(args.states_file, 'w')
    fo_t = open(args.trans_file, 'w')
    start_time = time.time()

    stateID = first_stateID
    last_nu = 0.    # the previous wavenumber read in
    percent_done = 0; percent_increment = 1     # for the progress indicator
    for i, line in enumerate(lines):

        # progress indicator, as a percentage
        percent = float(i)/ntrans * 100.
        if percent - percent_done > percent_increment:
            vprint('%d %%' % percent_done, 1)
            percent_done += percent_increment

        # parse the par_line into a HITRANTransition object
        trans = HITRANTransition.parse_par_line(line)

        if trans is None:
            # blank or comment line
            continue

        # check our wavenumbers are in order
        if trans.nu.val < last_nu:
            vprint('Error: %s transitions file isn\'t ordered by nu.'\
                    % args.trans_file, 5)
            sys.exit(1)
        last_nu = trans.nu.val

        # set the global (ie database-wide) ID for the isotopologue in
        # the transition and its upper and lower state objects
        trans.global_iso_id = args.global_iso_ids[
                                (trans.molec_id, trans.local_iso_id)]
        trans.statep.global_iso_id  = trans.global_iso_id
        trans.statepp.global_iso_id = trans.global_iso_id
        
        # first deal with the upper state: get its string representation ...
        statep_str_rep = trans.statep.str_rep()
        # ... and see if it's in our dictionary:
        if statep_str_rep in db_stateIDs.keys():
            # the upper state is already in the database: set the
            # corresponding state ID in the transition object
            trans.stateIDp = db_stateIDs[statep_str_rep]
        else:
            # the upper state is new: assign it an ID and save it
            trans.stateIDp = trans.statep.id = stateID
            db_stateIDs[statep_str_rep] = stateID
            stateID += 1
            print >>fo_s, statep_str_rep

        # next deal with the lower state: get its string representation ...
        statepp_str_rep = trans.statepp.str_rep()
        # ... and see if it's in our dictionary:
        if statepp_str_rep in db_stateIDs.keys():
            # the lower state is already in the database: set the
            # corresponding state ID in the transition object
            trans.stateIDpp = db_stateIDs[statepp_str_rep]
        else:
            # the lower state is new: assign it an ID and save it
            trans.stateIDpp = trans.statepp.id = stateID
            db_stateIDs[statepp_str_rep] = stateID
            stateID += 1
            print >>fo_s, statepp_str_rep

        # check that the references for this transition's parameters are in
        # the tables hitranmeta_refs_map and hitranmeta_source - if they    
        # aren't this is fatal, so we exit
        for j, prm_name in enumerate(['nu', 'S', 'gamma_air', 'gamma_self',
                                      'n_air', 'delta_air']):
            # the reference fields of the par_line are at character
            # positions 134-146 of the 160-byte par_line, in 2-character fields
            iref = int(trans.par_line[133+2*j:135+2*j])
            # work out which Source in hitranmeta_source this reference id
            # is pointing to, using the hitranmeta_refs_map table to map it
            # to a primary key in the hitranmeta_source table.
            if iref == 0:
                # don't worry about missing 0 refs (which default to the
                # HITRAN 1986 paper)
                source_id = HITRAN1986_SOURCEID
            else:
                # form a HITRAN-style source identifier as
                # <molecule_name>-<prm_name>-<id>, for looking up in the
                # hitranmeta_refs_map table
                sref = '%s-%s-%d' % (molecule.ordinary_formula,
                                     prm_name, iref)
                # we can't use '+' in XML attributes, so replace with 'p'
                sref = sref.replace('+', 'p')
                if sref not in d_refs.keys():
                    # Oops - missing reference: bail.
                    print 'missing reference for %s in hitranmeta_refs_map'\
                          ' table' % sref
                    sys.exit(1)
                # all's well - we have a valid source_id
                source_id = d_refs[sref].source_id

            # TODO avoid exec here
            # Assign the source_id to the parameter object
            if prm_name == 'S':
                exec('trans.Sw.source_id = %d' % source_id)
                exec('trans.A.source_id = %d' % source_id)
            else:
                try:
                    exec('trans.%s.source_id = %d' % (prm_name, source_id))
                except AttributeError:
                    # no parameter object exists for prm_name; this can
                    # happen if e.g. delta_air=0. and none was created, but
                    # it's fine- we just move on
                    pass

        # write the transition to the .trans file, *even if it is already
        # in the database* - this is checked for on upload
        print >>fo_t, trans.to_str(trans_fields, ',')

    fo_t.close()
    fo_s.close()
    vprint('%d new or updated states were identified'\
                    % (stateID-first_stateID))

    end_time = time.time()
    vprint('%d transitions and %d states in %.1f secs'\
                % (len(lines), len(db_stateIDs), end_time - start_time))
