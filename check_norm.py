#!/usr/bin/env python
# -*- coding: utf-8 -*-
# check_norm.py

# Christian Hill, 24/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to check the separated trans and states files produced by
# par2norm.py against the .par format they came from

import os
import sys

from pyHAWKS_config import *
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranmeta.models import Molecule, Iso 
from hitranlbl.models import State

import time
from hitran_cases import *
from hitran_transition import HITRANTransition
from hitran_param import HITRANParam
import hitran_meta
import xn_utils
from fmt_xn import *
from correct_par import *

filestem = sys.argv[1]

# get the Molecule and Iso objects from the molecID, taken from
# the par_file filename
try:
    molecID = int(filestem.split('_')[0])
except:
    print 'couldn\'t parse molecID from filestem %s' % filestem
    print 'the filename should start with "<molecID>_"'
    sys.exit(1)
molecule = Molecule.objects.filter(pk=molecID).get()
isos = Iso.objects.filter(molecule=molecule).order_by('isoID')
# map global isotopologue ID to local, HITRAN molecID and isoID
hitran_ids = {}
for iso in isos:
    hitran_ids[iso.id] = (iso.molecule.id, iso.isoID)

trans_file = os.path.join(DATA_DIR, '%s.trans' % filestem)
states_file = os.path.join(DATA_DIR, '%s.states' % filestem)
corrections_file = os.path.join(DATA_DIR, '%s.corrections' % filestem)

states = []
for line in open(states_file, 'r'):
    global_iso_id = int(line[:4])
    molec_id, local_iso_id = hitran_ids[global_iso_id]
    try:
        E = float(line[5:15])
    except (TypeError, ValueError):
        E = None
    try:
        g = int(line[16:21])
    except (TypeError, ValueError):
        g = None
    s_qns = line[22:].strip()
    CaseClass = hitran_meta.get_case_class(molec_id, local_iso_id)
    states.append(CaseClass(molec_id=molec_id, local_iso_id=local_iso_id,
                            global_iso_id=global_iso_id, E=E, g=g,
                            s_qns=s_qns))
print '%d states read in.' % (len(states))

def get_state(stateID):
    """
    Get the state with ID stateID - if this is greater than or equal to
    stateID_offset (ie its ID is higher than the highest already in the
    database), then it is a new state and we expect to find it in our
    states[] list. If it is less than stateID_offset, we need to retrieve it
    from the database.

    """
    if stateID < stateID_offset:
        state = State.objects.get(pk=stateID)
        # map the Django State object to an instance of the appropriate
        # CaseClass for this state
        global_iso_id = state.iso_id
        molec_id, local_iso_id = hitran_ids[global_iso_id]
        CaseClass = hitran_meta.get_case_class(molec_id, local_iso_id)
        return CaseClass(molec_id=molec_id, local_iso_id=local_iso_id,
                         global_iso_id=global_iso_id, E=state.energy,
                         g=state.g, s_qns=state.s_qns)
    else:
        return states[stateID - stateID_offset]

stateID_offset = State.objects.all().order_by('-id')[0].id + 1
trans = []
start_time = time.time()
line_no = 0
ncorrections = 0
co = open(corrections_file, 'w')
for line in open(trans_file, 'r'):
    line_no += 1
    line = line.rstrip()
    this_trans = HITRANTransition()
    # create the HITRANParam objects for the trans_prms parameters
    for prm_name in trans_prms:
        setattr(this_trans, prm_name, HITRANParam(None))
        #eval('this_trans.%s=HITRANParam(None)' % prm_name)
    fields = line.split(',')
    for i, output_field in enumerate(trans_fields):
        this_trans.set_param(output_field.name, fields[i], output_field.fmt)
    #print this_trans.stateIDp, this_trans.stateIDpp
    this_trans.statep = get_state(this_trans.stateIDp)
    this_trans.statepp = get_state(this_trans.stateIDpp)
    this_trans.case_module = hitran_meta.get_case_module(this_trans.molec_id,
                        this_trans.local_iso_id)
    if not this_trans.validate_as_par():
        this_trans.old_par_line = this_trans.par_line
        this_trans.par_line = correct_par(this_trans)
        if this_trans.validate_as_par():
            print >>co, '%d-%s' % (line_no, this_trans.old_par_line)
            print >>co, '%d+%s' % (line_no, this_trans.par_line)
            ncorrections += 1
        else:
            print this_trans.par_line,'\nfailed to validate! I produced:'
            print this_trans.get_par_str()
            sys.exit(1)
    trans.append(this_trans)
co.close()
print '%d transitions read in.' % (len(trans))

end_time = time.time()
print '%d transitions and %d states in %s' % (len(trans), len(states),
             xn_utils.timed_at(end_time - start_time))
print '%d corrections made to original .par file saved as %s'\
            % (ncorrections, corrections_file)
