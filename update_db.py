#!/usr/bin/env python
# -*- coding: utf-8 -*-
# update_db.py

# Christian Hill, 12/4/12
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to parse a given .par file in the native HITRAN2004+ format
# and extract the relevant data for update to the relational database.
# Only states and transitions that have changed from those already in the
# database are saved in .states and .trans files - ie this creates a patch.

# NB this program expects to find a directory
# $DATA_DIR = $HOME/research/HITRAN/data/hitran
# into which it puts the .states and .trans files.
# One must also specify the location of the Django HITRAN project's
# settings file - see below: $HOME/research/VAMDC/HITRAN/django/HITRAN

import os
import sys

HOME = os.getenv('HOME')
DATA_DIR = os.path.join(HOME, 'research/HITRAN/data/hitran')
SETTINGS_PATH = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection, transaction

import time
import datetime
import argparse
from hitran_transition import HITRANTransition
import hitran_meta
from hitran_param import HITRANParam
from fmt_xn import *
import xn_utils
from hitranmeta.models import Molecule, Iso, RefsMap, Case
from hitranlbl.models import State, Trans, Qns, Prm

dbname = 'hitran'

# command line arguments:
parser = argparse.ArgumentParser(description='Update the HITRAN MySQL'
            ' database with a patch from the provided .par file in'
            ' native HITRAN2004+ format')
parser.add_argument('par_file', metavar='<par_file>',
        help='the .par file, and root of the filenames <filestem>.states'
             ' and <filestem>.trans')
parser.add_argument('-p', '--parse_par', dest='parse_par',
        action='store_const', const=True, default=False,
        help='parse .par file to  .states and .trans files and exit')
parser.add_argument('-U', '--upload', dest='upload', action='store_const',
        const=True, default=False,
        help='actually upload the data to the database, expiring existing'\
             ' transitions for this molecule')
parser.add_argument('-u', '--upload_dry_run', dest='dry_run',
        action='store_const', const=True, default=False,
        help='dry-run: create the data structures and SQL INSERT statements'\
             ' but don\'t  actually upload the data to the database')
parser.add_argument('-O', '--overwrite', dest='overwrite',
        action='store_const', const=True, default=False,
        help='overwrite .states and .trans files, if present')
parser.add_argument('-s', '--sources', dest='attach_sources',
        action='store_const', const=True, default=False,
        help='attach source IDs to parameters')
parser.add_argument('-e', '--expire', dest='expire_file',
        nargs=1, help='.par file of old transitions to expire from database')
args = parser.parse_args()
overwrite = args.overwrite   # over-write any existing .states and .trans files
parse_par = args.parse_par   # parse the given .par file containing the update
upload = args.upload         # upload the data to the MySQL database
dry_run = args.dry_run    # do the upload as a dry-run, without changing the db
expire_file = args.expire_file  # optional .par file of transitions to expire
if expire_file:
    expire_file = expire_file[0]

attach_sources_opt = args.attach_sources    # attach sources to parameters
if dry_run:
    print 'Dry-run only: database won\'t be modified'
    upload = True
elif upload:
    print 'The real thing: database will be modified'
filestem, ext = os.path.splitext(args.par_file)
if ext not in ('', '.par'):
    print 'par_file must end in .par or be given without extension; I got:'
    print args.par_file
    sys.exit(1)
par_file = '%s.par' % filestem
if not os.path.exists(par_file):
    print 'par_file not found:', par_file
    sys.exit(1)
filestem = os.path.basename(filestem)

# get the Molecule and Iso objects from the molecID, taken from
# the par_file filename
try:
    molecID = int(filestem.split('_')[0])
except:
    print 'couldn\'t parse molecID from filestem %s' % filestem
    print 'the filename should start with "<molecID>_"'
    sys.exit(1)
molecule = Molecule.objects.filter(pk=molecID).get()
molec_name = molecule.ordinary_formula
isos = Iso.objects.filter(molecule=molecule).order_by('isoID')

# get the RefsMap objects for this molecule, which have
# refID <molec_name>-<prm_name>-<id>, but '+' replaced with p, e.g. NO+ -> NOp
refs = RefsMap.objects.all().filter(refID__startswith='%s-'
            % molec_name.replace('+','p'))
# a dictionary of references, keyed by refID, e.g. 'O2-gamma_self-2'
d_refs = {}
for ref in refs:
    d_refs[ref.refID]= ref
print refs.count(),'references found for', molec_name
missing_refs = set()

if not os.path.exists(par_file):
    print 'No such file: %s' % par_file
    sys.exit(1)

if not os.path.exists(DATA_DIR):
    print 'Oops. I want to put my .states and .trans files in directory:'
    print DATA_DIR
    print 'but it doesn\'t exist.'
    sys.exit(1)

mod_date = datetime.date.fromtimestamp(os.path.getmtime(par_file)).isoformat()
print 'From file modification date, taking the from-date to be', mod_date

# the output files will be:
# $DATA_DIR/<filestem>-YYYY-MM-DD.states and .trans
# where <filestem> is typically <molec_ID>_hit<yr> with <yr> the 2-digit
# year of the update, and YYYY-MM-DD is the modification date of the
# .par file
trans_file = os.path.join(DATA_DIR, '%s.%s.trans' % (filestem, mod_date))
states_file = os.path.join(DATA_DIR, '%s.%s.states' % (filestem, mod_date))

# find out the ID at which we can start adding states
first_stateID = State.objects.all().order_by('-id')[0].id + 1

def locate_state_in_db(state):
    """
    Try to find state in the database table modelled by the State class;
    returns None if the state isn't found, or the state's primary key id
    if it is.

    """
     
    # find all the states in the database with the same quantum numbers as
    # the state we're seeking:
    try:
        dbstates = State.objects.filter(iso=isos[state.iso_id-1])\
                            .filter(s_qns=state.serialize_qns())
    except IndexError:
        print 'unknown isotopologue with HITRAN isoID =', state.iso_id
        sys.exit(1)
    if not dbstates:
        return None
    for dbstate in dbstates:
        # look through the states to see if everything else matches:
        if dbstate.str_rep() == state.str_rep():
            return dbstate.id
    # nothing matched; return None
    #print dbstate.str_rep(), state.str_rep()
    return None

def create_trans_states():
    print 'Creating .trans and .states files...'
    print '%s\n-> %s\n   %s' % (par_file, trans_file, states_file)
    if not overwrite:
        # the .trans and .states files should not already exist
        for filename in (trans_file,states_file):
            if os.path.exists(filename):
                print 'File exists:\n%s\nAborting.' % filename
                sys.exit(1)

    # read the lines and rstrip them of the EOL characters. We don't lstrip
    # because we keep the space in front of molecIDs 1-9
    lines = [x.rstrip() for x in open(par_file, 'r').readlines()]
    states = {}
    fo_s = open(states_file, 'w')
    fo_t = open(trans_file, 'w')
    start_time = time.time()
    stateID = first_stateID

    found_states = 0
    found_trans = 0
    for i,line in enumerate(lines):       # XXX
        trans = HITRANTransition.parse_par_line(line)
        if trans is None:
            # blank or comment line
            continue

        new_trans = False
        # upper state
        this_stateID = locate_state_in_db(trans.statep)
        if this_stateID:
            # this state is already in the database; set trans.stateIDp
            trans.stateIDp = this_stateID
            found_states += 1
        else:
            # this state isn't in the database: keep track of it in states[]
            statep_str_rep = trans.statep.str_rep()
            if statep_str_rep not in states:
                # we've not seen this upper state before: save it and write it
                # to fo_s
                trans.stateIDp = stateID
                states[statep_str_rep] = stateID
                stateID += 1
                print >>fo_s, trans.statep.to_str(state_fields, ',')
            else:
                trans.stateIDp = states[statep_str_rep]
            # if a transition references a new state, it's a new transition
            new_trans = True
        # lower state
        this_stateID = locate_state_in_db(trans.statepp)
        if this_stateID:
            # this state is already in the database; set trans.stateIDpp
            trans.stateIDpp = this_stateID
            found_states += 1
        else:
            # this state isn't in the database: keep track of it in states[]
            statepp_str_rep = trans.statepp.str_rep()
            if statepp_str_rep not in states:
                # we've not seen this lower state before: save it and write it
                # to fo_s
                trans.stateIDpp = stateID
                states[statepp_str_rep] = stateID
                stateID += 1
                print >>fo_s, trans.statepp.to_str(state_fields, ',')
            else:
                trans.stateIDpp = states[statepp_str_rep]
            # if a transition references a new state, it's a new transition
            new_trans = True

        # check that the references are in the tables hitranmeta_ref and
        # hitranmeta_source
        for i, prm_name in enumerate(['nu', 'S', 'gamma_air', 'gamma_self',
                                      'n_air', 'delta_air']):
            iref = int(trans.par_line[133+2*i:135+2*i])
            if iref == 0:
                # don't worry about missing 0 refs (HITRAN 1986 paper)
                continue
            sref = '%s-%s-%d' % (molec_name, prm_name, iref)
            sref = sref.replace('+', 'p')  # we can't use '+' in XML attributes
            if sref not in d_refs.keys():
                missing_refs.add(sref)

        print >>fo_t, trans.to_str(trans_fields, ',')

        # if we're here, it's because the transition is already in the database
        found_trans += 1
        continue

    fo_t.close()
    fo_s.close()
    print '%d states were already in the database' % found_states
    print '%d new or updated states were identified' % (stateID-first_stateID)
    print '%d transitions were already in the database' % found_trans
    print 'References missing from the database are:'
    for missing_ref in missing_refs:
        print missing_ref

    end_time = time.time()
    print '%d transitions and %d states in %.1f secs'\
                % (len(lines), len(states), end_time - start_time)

def expire_old():
    print 'Expiring old transitions from', expire_file,'...'
    nold = 0
    old_par_lines = []
    for par_line in open(expire_file, 'r').readlines():
        old_par_lines.append(par_line.rstrip())
    old_transitions = Trans.objects.all().filter(par_line__in=old_par_lines)
    for old_trans in old_transitions:
        old_trans.valid_to = mod_date
        if not dry_run:
            old_trans.save()
    print old_transitions.count(), 'old lines expired'

def upload_to_db():
    print 'Uploading to database...'

    today = datetime.date.today()
    existing_transs = Trans.objects.all().filter(iso__in=isos)\
                                         .filter(valid_to__gt=today)
    print existing_transs.count(),'existing transitions in database'

    if expire_file:
        expire_old()
    else:
        print 'Expiring all old transitions...'
        for trans in existing_transs:
            trans.valid_to = mod_date
            if not dry_run:
                trans.save()

    # get the molecular state description 'cases' in a list indexed by caseID
    cases = Case.objects.all()
    cases_list = [None,]    # caseIDs start at 1, so case_list[0]=None
    for case in cases:
        cases_list.append(case)

    # read in, store, and upload the states from the .states file
    states = []
    start_time = time.time()
    for line in open(states_file, 'r'):
        fields = line.split(',')
        molec_id = int(fields[0])
        iso_id = int(fields[1])
        try:
            E = float(fields[2])
        except (TypeError, ValueError):
            E = None
        try:
            g = int(fields[3])
        except (TypeError, ValueError):
            g = None
        s_qns = fields[4].strip()
        if not s_qns:
            s_qns == None
        CaseClass = hitran_meta.get_case_class(molec_id, iso_id)
        # state is one of the hitran_case states (e.g. an HDcs object)
        state = CaseClass(molec_id=molec_id, iso_id=iso_id, E=E, g=g,
                           s_qns=s_qns)
        iso = isos[iso_id-1]

        # this_state is a hitranlbl.State object for the MySQL database
        this_state = State(iso=iso, energy=state.E, g=state.g,
                           s_qns=state.s_qns, qns_xml=state.get_qns_xml())
        if not dry_run:
            # if we're doing it for real, save the State just created
            this_state.save()
        states.append(this_state)

        # now create the quantum numbers entries for this state
        case = cases_list[state.__class__.caseID]
        for qn_name in state.__class__.ordered_qn_list:
            qn_val = state.get(qn_name)
            if qn_val is None:
                continue
            qn_attr = state.serialize_qn_attrs(qn_name)
            if qn_attr:
                # strip the initial '#'
                qn_attr = qn_attr[1:]
            else:
                qn_attr = None
            xml = state.get_qn_xml(qn_name)
            if not xml:
                xml = None
            qn = Qns(case=case, state=this_state, qn_name=qn_name,
                     qn_val=str(qn_val), qn_attr=qn_attr, xml=xml)
            if not dry_run:
                # if we're really uploading, save qn to the database
                qn.save()
    end_time = time.time()
    print '%d states read in (%s)' % (len(states),
                xn_utils.timed_at(end_time - start_time))

    # now read in and upload the transitions
    start_time = time.time()
    ntrans = 0
    for line in open(trans_file, 'r'):
        line = line.rstrip()
        trans = HITRANTransition()
        for prm_name in trans_prms:
            # create and attach the HITRANParam objects
            setattr(trans, prm_name, HITRANParam(None))
        fields = line.split(',')
        for i, output_field in enumerate(trans_fields):
            # set the transition attributes
            trans.set_param(output_field.name, fields[i], output_field.fmt)
        if trans.stateIDp < first_stateID:
            # this state is already in the database: find it
            trans.statep = State.objects.all().get(pk=trans.stateIDp)
        else:
            # new state: get it from the states list
            trans.statep = states[trans.stateIDp-first_stateID]
        if trans.stateIDpp < first_stateID:
            # this state is already in the database: find it
            trans.statepp = State.objects.all().get(pk=trans.stateIDpp)
        else:
            trans.statepp = states[trans.stateIDpp-first_stateID]
        trans.case_module = hitran_meta.get_case_module(trans.molec_id,
                            trans.iso_id)

        iso = isos[trans.iso_id-1]
        # this_trans is a hitranmeta.Trans object for the MySQL database
        this_trans = Trans(iso=iso, statep=trans.statep, statepp=trans.statepp,
                nu=trans.nu.val, Sw=trans.Sw.val, A=trans.A.val,
                multipole=trans.multipole, Elower=trans.Elower, gp=trans.gp,
                gpp=trans.gpp, valid_from=mod_date, par_line=trans.par_line)
        ntrans += 1
        if not dry_run:
            # if we're really uploading, save the transition to the database
            this_trans.save()
        
        # create the hitranlbl.Prm objects for this transition's parameters
        for prm_name in trans_prms:
            val = trans.get_param_attr(prm_name, 'val')
            if val is None:
                continue
            iref = trans.get_param_attr(prm_name, 'ref')
            ref=None
            if iref is not None:
                sref = '%s-%s-%d' % (molec_name, prm_name, iref)
                # we can't use '+' in XML attributes
                sref = sref.replace('+', 'p')
                # references to Sw refer to S
                sref = sref.replace('-Sw-', '-S-')
                # references to A are from S
                sref = sref.replace('-A-', '-S-')
                ref = d_refs.get(sref)
                if ref is None and iref !=0:
                    # ignore the common case of reference 0 missing
                    print 'Warning: %s does not exist' % sref
            if iref == 0:
                source_id = 1
            else:
                source_id = ref.source_id
            prm = Prm(trans=this_trans, name=prm_name,
                      val=val,
                      err=trans.get_param_attr(prm_name, 'err'),
                      ierr=trans.get_param_attr(prm_name, 'ierr'),
                      source_id=source_id)
            if not dry_run:
                # if we're really uploading, save the prm to the database
                prm.save()

    end_time = time.time()
    print '%d transitions read in (%s)' % (ntrans,
                xn_utils.timed_at(end_time - start_time))

def attach_sources():
    print 'attaching sources to parameters...'
    cursor = connection.cursor()
    command = 'UPDATE hitranlbl_prm p, hitranlbl_trans t,'\
              ' hitranmeta_refs_map r'\
              ' SET p.source_id=r.source_id WHERE'\
              ' t.valid_from="%s" AND t.iso_id IN (%s) AND p.trans_id=t.id'\
              ' AND p.ref_id=r.id' % (str(mod_date),
                                      ','.join([str(iso.id) for iso in isos]))
    print command
    cursor.execute(command)
    transaction.commit_unless_managed()

    return

### Main program starts here! ###

if parse_par:
    create_trans_states()
if upload:
    if missing_refs:
        # if we're trying to upload the data immediately after parsing the
        # par file, bail if there references haven't been entered into the db
        print 'can\'t update database when there are missing refs.'
        sys.exit(1)
    upload_to_db()

if attach_sources_opt:
    attach_sources()
