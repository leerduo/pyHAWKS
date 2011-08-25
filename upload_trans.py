#!/usr/bin/env python
# -*- coding: utf-8 -*-
# upload_trans.py

# Christian Hill, 24/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to upload transitions and states from a pair of .states and
# .trans files (output from par2norm.py) to the MySQL hitranlbl database.

import os
import sys
import time
import datetime
from hitran_cases import *
import hitran_meta

# Django needs to know where to find the SpeciesDB project's settings.py:
HOME = os.getenv('HOME')
hitran_path = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
sys.path.append(hitran_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from hitranmeta.models import *
from hitranlbl.models import *

HOME = os.getenv('HOME')
data_dir = os.path.join(HOME, 'research/HITRAN/data')
file_stem = sys.argv[1]

trans_file = os.path.join(data_dir, '%s.trans' % file_stem)
states_file = os.path.join(data_dir, '%s.states' % file_stem)

# the last 10 characters of file_stem are a datestamp in ISO 8601 format
valid_from_iso = file_stem[:-10]
# parse the datestamp YYYY-MM-DD into a datetime.date object
valid_from = datetime.date(*[int(x) for x in valid_from_iso.split('-')])

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
    iso = Iso.objects.filter(molecule__molecID=molec_id).filter(
                isoID=iso_id).get()
    # this_state is a hitranmeta.State object for the MySQL database
    this_state = State(iso=iso, energy=state.E, g=state.g, s_qns=state.s_qns,
                       qns_xml=state.get_qns_xml())
    states.append(this_state)
    case = Case.objects.filter(caseID=type(state).caseID).get()
    for qn_name in type(state).ordered_qn_list:
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
end_time = time.time()
print '%d states read in (%.1f secs)' % (len(states), (end_time - start_time))

start_time = time.time()
for line in open(trans_file, 'r'):
    line = line.rstrip()
    trans = HITRANTransition()
    for prm_name in trans_prms:
        setattr(trans, prm_name, HITRANParam(None))
    fields = line.split(',')
    for i,(prm_name, fmt, default) in enumerate(trans_fields):
        try:
            exec("trans.%s = %s(fields[%d])" % (prm_name, conv(fmt), i))
        except ValueError:
            exec('trans.%s = None' % prm_name)
    trans.statep = states[trans.stateIDp]
    trans.statepp = states[trans.stateIDpp]
    trans.case_module = hitran_meta.get_case_module(trans.molec_id,
                        trans.iso_id)

    iso = Iso.objects.filter(molecule__molecID=trans.molec_id).filter(
                isoID=trans.iso_id).get()
    statep = states[trans.stateIDp]
    statepp = states[trans.stateIDpp]
    this_trans = Trans(iso=iso, statep=statep, statepp=statepp,
            nu=trans.nu.val, Sw=trans.Sw.val, A=trans.A.val,
            multipole=trans.multipole, elower=trans.Elower, gp=trans.gp,
            gpp=trans.gpp, valid_from=valid_from)
    
    for prm_name in trans_prms:
        prm = Prm(trans=this_trans, name=prm_name, val=getattr(trans.
    