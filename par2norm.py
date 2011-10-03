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
from fmt_xn import *
from HITRAN_configs import dbname

molec_id = int(sys.argv[1])
par_name = '%02d_hit08.par' % molec_id

HOME = os.getenv('HOME')
# whether we're using hitran or minihitran, get the last modified date from
# the original par file
orig_par_dir = os.path.join(HOME, 'research/HITRAN/HITRAN2008/HITRAN2008/'\
                                  'By-Molecule/Uncompressed-files')
orig_par_path = os.path.join(orig_par_dir, par_name)
mod_date = datetime.date.fromtimestamp(os.path.getmtime(
                            orig_par_path)).isoformat()

if dbname.lower() == 'hitran':
    par_dir = orig_par_dir
    out_dir = os.path.join(HOME, 'research/HITRAN/data')
elif dbname.lower() == 'minihitran':
    par_dir = os.path.join(HOME, 'research/HITRAN/data/minihitran')
    out_dir = os.path.join(HOME, 'research/HITRAN/data/minihitran')
elif dbname.lower() == 'microhitran':
    par_dir = os.path.join(HOME, 'research/HITRAN/data/microhitran')
    out_dir = os.path.join(HOME, 'research/HITRAN/data/microhitran')
par_path = os.path.join(par_dir, par_name)

# the output files will be:
# $HOME/research/HITRAN/data/<par_name>-YYYY-MM-DD.states and .trans or
# $HOME/research/HITRAN/data/minihitran/<par_name>-YYYY-MM-DD.states and .trans
# where <par_name> is <molec_ID>_hit08 and is appended with the modification
# date of the original .par file
trans_name = '%s.%s.trans' % (par_name[:-4], mod_date)
states_name = '%s.%s.states' % (par_name[:-4], mod_date)
print '%s -> (%s, %s)' % (par_name, trans_name, states_name)

def str_rep(state):
    """ A helper function to return a string representation of the state."""
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

# read the lines and rstrip them of the EOL characters. We don't lstrip
# because we keep the space in front of molecIDs 1-9
lines = [x.rstrip() for x in open(par_path, 'r').readlines()]
states = {}
out_states = open(os.path.join(out_dir, states_name), 'w')
out_trans = open(os.path.join(out_dir, trans_name), 'w')
start_time = time.time()
stateID = 0
for i,line in enumerate(lines):
    trans = HITRANTransition.parse_par_line(line)
    if trans is None:
        # blank or comment line
        continue

    statep_str_rep = str_rep(trans.statep)
    if statep_str_rep not in states:
        # we've not seen this upper state before: save it and write it
        # to out_states
        trans.stateIDp = stateID
        states[statep_str_rep] = stateID
        stateID += 1
        print >>out_states, trans.statep.to_str(state_fields, ',')
    else:
        trans.stateIDp = states[statep_str_rep]
    statepp_str_rep = str_rep(trans.statepp)
    if statepp_str_rep not in states:
        # we've not seen this lower state before: save it and write it
        # to out_states
        trans.stateIDpp = stateID
        states[statepp_str_rep] = stateID
        stateID += 1
        print >>out_states, trans.statepp.to_str(state_fields, ',')
    else:
        trans.stateIDpp = states[statepp_str_rep]

    print >>out_trans, trans.to_str(trans_fields, ',')

out_trans.close()
out_states.close()

end_time = time.time()
print '%d transitions and %d states in %.1f secs' % (len(lines), len(states),
            end_time - start_time)
