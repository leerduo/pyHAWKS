#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_nucspin.py

# Christian Hill, 25/1/12
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to set the nucspin_label of the hitranlbl_state table for
# nonlinear triatomic molecules of appropriate symmetry such as H2O.

import os
import sys

# Django needs to know where to find the HITRAN project's settings.py:
HOME = os.getenv('HOME')
hitran_path = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
sys.path.append(hitran_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from hitranmeta.models import *
from hitranlbl.models import *

iso_name = 'H2(16O)'
iso = Iso.objects.filter(iso_name=iso_name).get()
print iso.iso_name, iso.isoID
states = State.objects.filter(iso=iso)
print '%d states for %s found.' % (states.count(), iso_name)

northo = 0; npara = 0
ortho = para = False
for state in states:
    qns = Qns.objects.filter(state=state).filter(qn_name__in=['v3', 'Ka', 'Kc']).values_list('qn_val', flat=True)
    if qns.count() != 3:
        # one or more of v3, Ka, Kc is missing; we can't assign a nuclear spin
        # label in this case
        continue
    tot = 0
    for qn in qns:
        tot += int(qn)
    if tot % 2:   
        northo += 1
        #print qns, 'is ortho'
        para = False; ortho = True
    else:
        npara += 1
        #print qns, 'is para'
        ortho = False; para = True
    if ortho:
        print "UPDATE hitran2.hitranlbl_state SET nucspin_label='o'"\
              " WHERE id = %d" % state.id
    elif para:
        print "UPDATE hitran2.hitranlbl_state SET nucspin_label='p'"\
              " WHERE id = %d" % state.id
print 'northo = %d; npara =%d' % (northo, npara)

