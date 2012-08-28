#!/usr/bin/env python
# recalc_A.py
# recalculate the Einstein A coefficients in a HITRAN .par file from
# its Sw, weighted line intensity value
import os
import sys
import math
import physcon as pc
from hitran_transition import HITRANTransition

c2 = pc.h * pc.c * 100. / pc.kB     # second radiation constant, cm.K
pic8 = 8. * math.pi * pc.c * 100    # 8.pi.c in cm-1 s

T = 296.
Q = 1725.235188     # XXX for NH3 only!

def calc_A(nu0, Epp, gp, Sw, Q, T, abundance):
    c2oT = c2 / T
    A = pic8 * nu0**2 * Q * Sw / gp / math.exp(-c2oT * Epp) /\
            (1 - math.exp(-c2oT * nu0)) / abundance
    return A

HOME = os.getenv('HOME')
hitran_path = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
sys.path.append(hitran_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from hitranmeta.models import *
isos = Iso.objects.all()
abundances = {}
for iso in isos:
    abundances['%2d%1d' % (iso.molecule_id, iso.isoID)] = iso.abundance

par_dir = os.path.join(HOME, 'research/HITRAN/HITRAN2008/HITRAN2008/'\
                                  'By-Molecule/Uncompressed-files')
par_name = sys.argv[1]
par_path = os.path.join(par_dir, par_name)
lines = [x.rstrip() for x in open(par_path, 'r').readlines()]
for i,line in enumerate(lines):
    trans = HITRANTransition.parse_par_line(line)
    if trans is None:
        # blank or comment line
        continue
    if trans.gp is None:
        print 'unassigned line at %12.6f' % trans.nu.val
        continue
    A = calc_A(trans.nu.val, trans.Elower, trans.gp, trans.Sw.val, Q, T,
               abundances[trans.par_line[:3]])
    if trans.par_line[25:35] != '%10.3E' % A:
        #print trans.par_line[25:35], '%10.3E' % A
        print '%10.3E %10.3E' % (trans.A.val, A)
    #if i > 10:
    #    sys.exit(0)
    
    

