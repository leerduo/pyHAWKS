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
import argparse
from hitran_cases import *
from hitran_transition import HITRANTransition
from hitran_param import HITRANParam
import hitran_meta
from fmt_xn import *
import xn_utils
from HITRAN_configs import dbname

# command line arguments:
parser = argparse.ArgumentParser(description='Upload some transitions'
            ' from a pair of parsed .trans, .states files')
parser.add_argument('-u', '--upload', dest='upload', action='store_const',
        const=True, default=False,
        help='actually upload the data to the database')
parser.add_argument('-i', '--inserts', dest='insert', action='store_const',
        const=True, default=False,
        help='write the MySQL insert commands but don\'t execute them')
parser.add_argument('file_stem', metavar='<filestem>',
        help='the root of the filenames <filestem>.states'
             ' and <filestem>.trans')
args = parser.parse_args()
upload = args.upload
insert = args.insert
file_stem = args.file_stem

# Django needs to know where to find the HITRAN project's settings.py:
HOME = os.getenv('HOME')
hitran_path = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
sys.path.append(hitran_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from hitranmeta.models import *
from hitranlbl.models import *

print 'using database:', dbname

if dbname.lower() == 'hitran':
    data_dir = os.path.join(HOME, 'research/HITRAN/data/hitran')
elif dbname.lower() == 'minihitran':
    data_dir = os.path.join(HOME, 'research/HITRAN/data/minihitran')
elif dbname.lower() == 'microhitran':
    data_dir = os.path.join(HOME, 'research/HITRAN/data/microhitran')

trans_file = os.path.join(data_dir, '%s.trans' % file_stem)
states_file = os.path.join(data_dir, '%s.states' % file_stem)

# the last 10 characters of file_stem are a datestamp in ISO 8601 format
valid_from_iso = file_stem[-10:]
# parse the datestamp YYYY-MM-DD into a datetime.date object
valid_from = datetime.date(*[int(x) for x in valid_from_iso.split('-')])
# the HITAN molecule ID is the first two characters of file_stem
molecID = int(file_stem[:2])
molec_name = Molecule.objects.filter(molecID=molecID).get().ordinary_formula

# get all the references for this molecule
s = molec_name
s.replace('+', 'p')
s = '%s-' % s
refs = Ref.objects.filter(refID__startswith=s)
refs_dict = {}
for ref in refs:
    refs_dict[ref.refID] = ref

# get all the isotopologues for this molecule
isos = Iso.objects.filter(molecule__molecID=molecID)
isos_dict = {}
for iso in isos:
    # key isos_dict by HITRAN isotopologue integer id
    isos_dict[iso.isoID] = iso

# get the cases for this molecule's states
cases = Case.objects.all()
cases_list = [None,]
for case in cases:
    cases_list.append(case)

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
    iso = isos_dict[iso_id]

    # this_state is a hitranmeta.State object for the MySQL database
    this_state = State(iso=iso, energy=state.E, g=state.g, s_qns=state.s_qns,
                       qns_xml=state.get_qns_xml())
    if upload:
        this_state.save()
    states.append(this_state)
    #case = Case.objects.filter(pk=state.__class__.caseID).get()
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
        if upload:
            qn.save()
end_time = time.time()
print '%d states read in (%s)' % (len(states),
            xn_utils.timed_at(end_time - start_time))

start_time = time.time()
ntrans = 0
for line in open(trans_file, 'r'):
    line = line.rstrip()
    trans = HITRANTransition()
    for prm_name in trans_prms:
        # create the HITRANParam objects
        setattr(trans, prm_name, HITRANParam(None))
    fields = line.split(',')
    for i, output_field in enumerate(trans_fields):
        # set the transition attributes
        trans.set_param(output_field.name, fields[i], output_field.fmt)
    trans.statep = states[trans.stateIDp]
    trans.statepp = states[trans.stateIDpp]
    trans.case_module = hitran_meta.get_case_module(trans.molec_id,
                        trans.iso_id)

    iso = isos_dict[trans.iso_id]
    #iso = Iso.objects.filter(molecule__molecID=trans.molec_id).filter(
    #            isoID=trans.iso_id).get()
    statep = states[trans.stateIDp]
    statepp = states[trans.stateIDpp]
    # this_trans is a hitranmeta.Trans object for the MySQL database
    this_trans = Trans(iso=iso, statep=statep, statepp=statepp,
            nu=trans.nu.val, Sw=trans.Sw.val, A=trans.A.val,
            multipole=trans.multipole, Elower=trans.Elower, gp=trans.gp,
            gpp=trans.gpp, valid_from=valid_from, par_line=trans.par_line)
    ntrans += 1
    if upload:
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
            sref = sref.replace('+', 'p')  # we can't use '+' in XML attributes
            sref = sref.replace('-Sw-', '-S-') # references to Sw refer to S
            sref = sref.replace('-A-', '-S-')  # references to A are from S
            ref = refs_dict.get(sref)
            #try:
            #    ref = Ref.objects.filter(refID=sref).get()
            #except Ref.DoesNotExist:
            #    if iref != 0 :
            if ref is None and iref !=0:
                # ignore the common case of reference 0 missing
                print 'Warning: %s does not exist' % sref
                print 'val =',val
                #ref = None
        prm = Prm(trans=this_trans, name=prm_name,
                  val=val,
                  err=trans.get_param_attr(prm_name, 'err'),
                  ref=ref)
        if upload:
            prm.save()

end_time = time.time()
print '%d transitions read in (%s)' % (ntrans,
            xn_utils.timed_at(end_time - start_time))
