# -*- coding: utf-8 -*-
# upload_data.py

# v0.2
# Christian Hill, 6/8/12
#
# Upload the transitions from the staged files, either as a dry-run (the
# database is not changed) or for real.
#
# NB for future molecules, make sure that the HITRAN-specific molecular
# quantum number 'cases' have the right quantum numbers in them - e.g. the
# asymcs case only has an ordered list of quantum numbers containing
# vibrational modes up to v12.

import os
import sys
import time
import datetime
from xn_utils import vprint, timed_at
from pyHAWKS_config import SETTINGS_PATH, HITRAN1986_SOURCEID
import hitran_meta
from fmt_xn import trans_prms, trans_fields
from hitran_transition import HITRANTransition
from hitran_param import HITRANParam
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranmeta.models import Case, Source
from hitranlbl.models import State, Qns, Trans, Prm

def expire_old_transitions(args):
    """
    Expire the old transitions with ids given in the file named
    args.db_expire_id; that is, set their 'valid_to' attribute to the
    day before the mod_date of the data we're uploading.

    """

    vprint('expiring old transitions ...')
    # expire_date is to be the day before the modification date of the
    # par file we're uploading:
    expire_date = args.mod_date - datetime.timedelta(1)
    s_expire_date = expire_date.isoformat()
    # read in the IDs of the transitions to expire
    fi_ids = open(args.db_expire_id, 'r')
    for line in fi_ids.readlines():
        expire_id = int(line)
        trans = Trans.objects.all().filter(pk=expire_id).get()
        # set the new expiry date...
        trans.valid_to = s_expire_date
        # ... and save unless we're doing a dry-run
        if not args.dry_run:
            trans.save()
    fi_ids.close()
    vprint('done.')

def upload_states(args, isos, cases_list):
    """
    Read in, store, and upload the states to enter the database from the
    .states file.

    Arguments:
    args: the processed command line arguments with the names of files to
    use in uploading the data, the list of HITRAN molecule and isotopologue
    IDs to resolve the global_iso_id to etc...
    isos: a list of Iso objects, ordered by their local isotopologue ID
    cases_list: a list of Case objects, where the index is the case_id (ie
    cases_list[0] is None, cases_list[1] represents the dcs case etc...

    Returns:
    a list of the State objects uploaded.

    """

    vprint('Uploading states...')
    # the uploaded states will be stored in this list:
    states = []
    start_time = time.time()
    for line in open(args.states_file, 'r'):
        global_iso_id = int(line[:4])

        # state energy
        try:
            E = float(line[5:15])
        except (TypeError, ValueError):
            # undefined energy for this state
            E = None

        # state degeneracy
        try:
            g = int(line[16:21])
        except (TypeError, ValueError):
            # undefined degeneracy for this state
            g = None

        # state quantum numbers as a string of ';' separated name=value pairs
        s_qns = line[22:].strip()
        if not s_qns:
            # no quantum numbers resolved for this state
            s_qns == None

        # the native HITRAN IDs for molecule and isotopologue:
        molec_id, local_iso_id = args.hitran_ids[global_iso_id]

        # get the right Class to use to describe this state
        CaseClass = hitran_meta.get_case_class(molec_id, local_iso_id)
        # state is one of the hitran_case states (e.g. an HDcs object)
        state = CaseClass(molec_id=molec_id, local_iso_id=local_iso_id,
                          global_iso_id=global_iso_id, E=E, g=g, s_qns=s_qns)
        # retrieve the correct Iso object for this isotopologue
        iso = isos[local_iso_id-1]

        # this_state is a hitranlbl.State object for the MySQL database
        this_state = State(iso=iso, energy=state.E, g=state.g,
                           s_qns=state.s_qns, qns_xml=state.get_qns_xml())
        if not args.dry_run:
            # if we're doing it for real, save the State just created
            this_state.save()

        states.append(this_state)

        # now create the quantum numbers entries for this state
        case = cases_list[state.__class__.caseID]
        # loop over all the possible quantum number names for this case
        # XXX this will fail to include all of the quantum numbers if
        # the case does not have the right quantum numbers in its
        # ordered_qn_list (e.g. asymcs currently only goes to v12...)
        for qn_name in state.__class__.ordered_qn_list:
            # get the value of this quantum number
            qn_val = state.get(qn_name)
            if qn_val is None:
                # if the quantum number isn't defined, move to the next one
                continue
            # get any attribute metadata for this quantum number
            qn_attr = state.serialize_qn_attrs(qn_name)
            if qn_attr:
                # strip the initial '#'
                qn_attr = qn_attr[1:]
            else:
                qn_attr = None

            # get the XML for this quantum number
            xml = state.get_qn_xml(qn_name)
            if not xml:
                xml = None

            # create the quantum number object ...
            qn = Qns(case=case, state=this_state, qn_name=qn_name,
                     qn_val=str(qn_val), qn_attr=qn_attr, xml=xml)
            if not args.dry_run:
                # ... and save it to the database if we're not on a dry run
                qn.save()

    end_time = time.time()
    vprint('%d states read in (%s)' % (len(states),
                timed_at(end_time - start_time)))
    return states

def get_sources(d_refs):
    """
    Given d_refs, a dictionary of hitranmeta_refs_map objects keyed by
    native HITRAN-style reference strings (e.g. 'O2-gamma_self-2'),
    create and return a dictionary of Source objects keyed by their primary
    key source_ids.

    """
    # always include the HITRAN 1986 default reference
    sources = {HITRAN1986_SOURCEID: Source.objects.filter(
                            pk=HITRAN1986_SOURCEID).get(),}
    for refID, ref_map in d_refs.items():
        sources[ref_map.source_id] = Source.objects.all()\
                            .filter(pk=ref_map.source_id).get()
    return sources

def upload_data(args, molecule, isos, d_refs):
    """
    Upload the new transitions and states to the database. Only do this for
    real if args.dry_run = False.

    Arguments:
    args: the processed command line arguments with the names of files to
    use in uploading the data, the list of HITRAN molecule and isotopologue
    IDs to resolve the global_iso_id to etc...
    molecule: the Molecule object for the molecule whose transitions and
    states are to be uploaded.
    isos: a list of Iso objects, ordered by their local isotopologue ID
    cases_list: a list of Case objects, where the index is the case_id (ie
    cases_list[0] is None, cases_list[1] represents the dcs case etc...
    d_refs: a dictionary of RefsMap objects, keyed by HITRAN-style refID,
    e.g. 'O2-gamma_self-2'.

    """

    vprint('Uploading to database...')

    # first, expire old lines
    expire_old_transitions(args)

    # get the all the molecular state description 'cases' in a list indexed
    # by caseID
    cases = Case.objects.all()
    cases_list = [None,]    # caseIDs start at 1, so case_list[0]=None
    for case in cases:
        cases_list.append(case)

    # find out the ID at which we can start adding states
    try:
        first_stateID = State.objects.all().order_by('-id')[0].id + 1
    except IndexError:
        # no states in the database yet, so we start at 1
        first_stateID = 1
    vprint('new states will be added with ids starting at %d' % first_stateID)

    # upload the new states
    states = upload_states(args, isos, cases_list)

    # get the Source objects we'll need to attach to the parameters
    sources = get_sources(d_refs)
    # this is the default Source for when we can't find anything better:
    hitran86_source = Source.objects.all().filter(pk=HITRAN1986_SOURCEID).get()

    # now read in and upload the transitions
    vprint('Uploading transitions ...')
    start_time = time.time()
    ntrans = 0
    for line in open(args.trans_file_upload, 'r'):
        line = line.rstrip() # strip the EOL because the last field is par_line
        trans = HITRANTransition()

        for prm_name in trans_prms:
            # create and attach the HITRANParam objects
            setattr(trans, prm_name, HITRANParam(None))
        fields = line.split(',')
        for i, output_field in enumerate(trans_fields):
            # set the transition attributes
            trans.set_param(output_field.name, fields[i], output_field.fmt)

        # attach the upper state to the transition
        if trans.stateIDp < first_stateID:
            # this state is already in the database: find it
            trans.statep = State.objects.all().get(pk=trans.stateIDp)
        else:
            # new upper state: get it from the states list
            trans.statep = states[trans.stateIDp-first_stateID]

        # attach the lower state to the transition
        if trans.stateIDpp < first_stateID:
            # this state is already in the database: find it
            trans.statepp = State.objects.all().get(pk=trans.stateIDpp)
        else:
            # new lower state: get it from the states list
            trans.statepp = states[trans.stateIDpp-first_stateID]

        # attach the case_module for this transition's states' quantum numbers
        trans.case_module = hitran_meta.get_case_module(trans.molec_id,
                            trans.local_iso_id)

        # fetch the right Iso object
        iso = isos[trans.local_iso_id-1]
        # this_trans is a hitranmeta.Trans object for the MySQL database
        this_trans = Trans(iso=iso, statep=trans.statep, statepp=trans.statepp,
                nu=trans.nu.val, Sw=trans.Sw.val, A=trans.A.val,
                multipole=trans.multipole, Elower=trans.Elower, gp=trans.gp,
                gpp=trans.gpp, valid_from=args.s_mod_date,
                par_line=trans.par_line)
        ntrans += 1
        if not args.dry_run:
            # if we're really uploading, save the transition to the database
            this_trans.save()
        
        # create the hitranlbl.Prm objects for this transition's parameters
        # XXX change this!
        for prm_name in trans_prms:
            val = trans.get_param_attr(prm_name, 'val')
            if val is None:
                # no value for this parameter - move on to the next one
                continue
            # fetch the Source object for this parameter
            source_id = trans.get_param_attr(prm_name, 'source_id')
            if source_id is not None:
                source = sources[source_id]
            else:
                # if we can't identify source_id, it's missing from the
                # hitranmeta_refs_map and/or hitransmeta_source tables:
                # this is fatal and we must exit with an error
                print 'Error! no reference specified for', prm_name
                sys.exit(1)

            # create the Prm object for this parameter - XXX change this
            prm = Prm(trans=this_trans,
                      name=prm_name,
                      val=val,
                      err=trans.get_param_attr(prm_name, 'err'),
                      ierr=trans.get_param_attr(prm_name, 'ierr'),
                      source=source)
            if not args.dry_run:
                # if we're really uploading, save the prm to the database
                prm.save()

    end_time = time.time()
    vprint('%d transitions read in (%s)' % (ntrans,
                timed_at(end_time - start_time)))

