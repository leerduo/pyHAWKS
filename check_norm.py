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
import time
from hitran_cases import *
from hitran_transition import HITRANTransition
from hitran_param import HITRANParam
import hitran_meta
import xn_utils
from fmt_xn import *
from correct_par import *
from HITRAN_configs import dbname

HOME = os.getenv('HOME')
if dbname.lower() == 'hitran':
    data_dir = os.path.join(HOME, 'research/HITRAN/data')
elif dbname.lower() == 'minihitran':
    data_dir = os.path.join(HOME, 'research/HITRAN/data/minihitran')
elif dbname.lower() == 'microhitran':
    data_dir = os.path.join(HOME, 'research/HITRAN/data/microhitran')
file_stem = sys.argv[1]

trans_file = os.path.join(data_dir, '%s.trans' % file_stem)
states_file = os.path.join(data_dir, '%s.states' % file_stem)
corrections_file = os.path.join(data_dir, '%s.corrections' % file_stem)

states = []
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
    CaseClass = hitran_meta.get_case_class(molec_id, iso_id)
    states.append(CaseClass(molec_id=molec_id, iso_id=iso_id, E=E, g=g,
                       s_qns=s_qns))
print '%d states read in.' % (len(states))

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
    this_trans.statep = states[this_trans.stateIDp]
    this_trans.statepp = states[this_trans.stateIDpp]
    this_trans.case_module = hitran_meta.get_case_module(this_trans.molec_id,
                        this_trans.iso_id)
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
