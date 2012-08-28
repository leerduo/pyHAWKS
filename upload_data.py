# -*- coding: utf-8 -*-
# upload_data.py

# v0.2
# Christian Hill, 6/8/12
#
# Upload the transitions from the staged files, either as a dry-run or
# for real.

import os
import sys
import time
import datetime
import xn_utils
vprint = xn_utils.vprint
from pyHAWKS_config import SETTINGS_PATH
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
    expire_date = args.mod_date - datetime.timedelta(1)
    s_expire_date = expire_date.isoformat()
    fi_ids = open(args.db_expire_id, 'r')
    for line in fi_ids.readlines():
        expire_id = int(line)
        trans = Trans.objects.all().filter(pk=expire_id).get()
        trans.valid_to = s_expire_date
        if not args.dry_run:
            trans.save()
    fi_ids.close()
    vprint('done.')

def upload_states(args, isos, cases_list):
    # read in, store, and upload the states from the .states file

    vprint('Uploading states...')
    states = []
    start_time = time.time()
    for line in open(args.states_file, 'r'):
        global_iso_id = int(line[:4])
        try:
            E = float(line[5:15])
        except (TypeError, ValueError):
            E = None
        try:
            g = int(line[16:21])
        except (TypeError, ValueError):
            g = None
        s_qns = line[22:].strip()
        if not s_qns:
            s_qns == None
        molec_id, local_iso_id = args.hitran_ids[global_iso_id]
        CaseClass = hitran_meta.get_case_class(molec_id, local_iso_id)
        # state is one of the hitran_case states (e.g. an HDcs object)
        state = CaseClass(molec_id=molec_id, local_iso_id=local_iso_id,
                          global_iso_id=global_iso_id, E=E, g=g, s_qns=s_qns)
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
            if not args.dry_run:
                # if we're really uploading, save qn to the database
                qn.save()
    end_time = time.time()
    vprint('%d states read in (%s)' % (len(states),
                xn_utils.timed_at(end_time - start_time)))
    return states

def get_sources(d_refs):
    # start with HITRAN 86 reference
    sources = {1: Source.objects.filter(pk=1).get(),}
    for refID, ref_map in d_refs.items():
        sources[ref_map.source_id] = Source.objects.all()\
                            .filter(pk=ref_map.source_id).get()
    return sources

def upload_data(args, molecule, isos, d_refs):
    vprint('Uploading to database...')

    # first, expire old lines
    expire_old_transitions(args)

    # get the molecular state description 'cases' in a list indexed by caseID
    cases = Case.objects.all()
    cases_list = [None,]    # caseIDs start at 1, so case_list[0]=None
    for case in cases:
        cases_list.append(case)

    # find out the ID at which we can start adding states
    try:
        first_stateID = State.objects.all().order_by('-id')[0].id + 1
    except IndexError:
        first_stateID = 1
    vprint('new states will be added with ids starting at', first_stateID)

    states = upload_states(args, isos, cases_list)

    sources = get_sources(d_refs)
    hitran86_source = Source.objects.all().filter(pk=1).get()

    # now read in and upload the transitions
    vprint('Uploading transitions ...')
    start_time = time.time()
    ntrans = 0
    for line in open(args.trans_file_upload, 'r'):
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
            # new upper state: get it from the states list
            trans.statep = states[trans.stateIDp-first_stateID]
        if trans.stateIDpp < first_stateID:
            # this state is already in the database: find it
            trans.statepp = State.objects.all().get(pk=trans.stateIDpp)
        else:
            # new lower state: get it from the states list
            trans.statepp = states[trans.stateIDpp-first_stateID]
        trans.case_module = hitran_meta.get_case_module(trans.molec_id,
                            trans.local_iso_id)

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
        for prm_name in trans_prms:
            val = trans.get_param_attr(prm_name, 'val')
            if val is None:
                continue
            source_id = trans.get_param_attr(prm_name, 'source_id')
            if source_id is not None:
                source = sources[source_id]
            else:
                print 'Error! no reference specified for', prm_name
                sys.exit(1)
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
                xn_utils.timed_at(end_time - start_time)))

