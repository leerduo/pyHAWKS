#!/usr/bin/env python
# -*- coding: utf-8 -*-
# par2norm.py

# Christian Hill, 24/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to parse a given .par file in the native HITRAN2004+ format
# and extract the relevant data for upload to the relational database.

import os
import sys
import time
import datetime
from hitran_transition import HITRANTransition
HOME = os.getenv('HOME')
par_dir = os.path.join(HOME, 'research/HITRAN/HITRAN2008/HITRAN2008/'\
                             'By-Molecule/Uncompressed-files')

out_dir = os.path.join(HOME, 'research/HITRAN/data')
molec_id = int(sys.argv[1])
par_name = '%02d_hit08.par' % molec_id
par_path = os.path.join(par_dir, par_name)
mod_date = datetime.date.fromtimestamp(os.path.getmtime(par_path)).isoformat()
trans_name = '%s.%s.trans' % (par_name[:-4], mod_date)
states_name = '%s.%s.states' % (par_name[:-4], mod_date)
print '%s -> (%s, %s)' % (par_name, trans_name, states_name)

state_fields = [('molec_id', '%2d', '  '), ('iso_id', '%1d', ' '),
                ('E', '%10.4f', ' '*10),
                ('g', '%5d', ' '*5), ('serialize_qns()', '%s', '')]
trans_fields = [('molec_id', '%2d', '  '), ('iso_id', '%1d', ' '),
                ('nu.val', '%12.6f', ' '*12),
                ('Sw.val', '%10.3e', ' '*10), ('A.val', '%10.3e', ' '*10),
                ('gamma_air.val', '%6.4f', ' '*6),
                ('gamma_self.val', '%6.4f', ' '*6),
                ('n_air.val', '%5.2f', ' '*5),
                ('delta_air.val', '%9.6f', ' '*9),
                ('stateIDp', '%12d', ' '*12), ('stateIDpp', '%12d', ' '*12)]

def str_rep(state):
    try:
        s_g = '%5d' % state.g
    except TypeError:
        s_g = ''
    try:
        s_E = '%10.4f' % state.E
    except TypeError:
        s_E = ''
    return '%2d%1d%s%s%s' % (state.molec_id, state.iso_id, s_E,
            s_g, state.serialize_qns())

lines = [x.rstrip() for x in open(par_path, 'r').readlines()]
states = {}
out_states = open(os.path.join(out_dir, states_name), 'w')
out_trans = open(os.path.join(out_dir, trans_name), 'w')
start_time = time.time()
stateID = 0
for i,line in enumerate(lines):
    trans = HITRANTransition.parse_par_line(line)
    statep_str_rep = str_rep(trans.statep)
    if statep_str_rep not in states:
        trans.stateIDp = stateID
        states[statep_str_rep] = stateID
        stateID += 1
        print >>out_states, trans.statep.to_str(state_fields)
    else:
        trans.stateIDp = states[statep_str_rep]
    statepp_str_rep = str_rep(trans.statepp)
    if statepp_str_rep not in states:
        trans.stateIDpp = stateID
        states[statepp_str_rep] = stateID
        stateID += 1
        print >>out_states, trans.statepp.to_str(state_fields)
    else:
        trans.stateIDpp = states[statepp_str_rep]
    print >>out_trans, trans.to_str(trans_fields)

out_trans.close()
out_states.close()

end_time = time.time()
print '%d transitions and %d states in %.1f secs' % (len(lines), len(states),
            end_time - start_time)
