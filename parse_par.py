#!/usr/bin/env python
# -*- coding: utf-8 -*-
# parse_par.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to parse a given .par file in the native HITRAN2004+ format
# and extract the relevant data for upload to the relational database.

import os
import sys
import time
from hitran_transition import HITRANTransition
HOME = os.getenv('HOME')
par_dir = os.path.join(HOME, 'research/HITRAN/HITRAN2008/HITRAN2008/'\
                             'By-Molecule/Uncompressed-files')

molec_id = int(sys.argv[1])
par_name = '%02d_hit08.par' % molec_id
print par_name

par_path = os.path.join(par_dir, par_name)
lines = [x.rstrip() for x in open(par_path, 'r').readlines()]
states = set()
start_time = time.time()
for i,line in enumerate(lines):
    trans = HITRANTransition.parse_par_line(line)
    if trans:
    #    states.add(trans.statepp)
    #    states.add(trans.statep)
        pass
    else:
        print 'BAD TRANSITION'
    #print trans.par_line
    #print trans.get_par_str()
    if not trans.validate_as_par():
        print trans.par_line,'\nfailed to validate!'
    #print trans.statep.serialize_qns()
    #if i > 100: break   
end_time = time.time()
print 'time: %.1f secs' % (end_time - start_time)
print len(lines)
print len(states)




