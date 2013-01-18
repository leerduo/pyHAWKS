#!/usr/bin/env python
# -*- coding: utf-8 -*-
# set_band.py
# Christian Hill, 7/1/13
# Set the band column of hitranlbl_trans for a given molecule, indicating
# the vibrational band that each transition belongs to.

import os
import sys
import re
SETTINGS_PATH = '/Users/christian/research/VAMDC/HITRAN/django/HITRAN'
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranmeta.models import Molecule, Iso
from hitranlbl.models import State, Trans, Qns
from django.db import connection

cursor = connection.cursor()

# get the Molecule object for the requested molecule
try:
    ordinary_formula = sys.argv[1]
    molecule = Molecule.objects.get(ordinary_formula=ordinary_formula)
except (IndexError, Molecule.DoesNotExist):
    print 'usage:\n%s <ordinary_formula>' % sys.argv[0]
    sys.exit(1)

# also get the Isotopologue objects for this Molecule:
isos = Iso.objects.filter(molecule=molecule)
print '%d isotopologues of %s found' % (isos.count(), ordinary_formula)

def get_vib_qns_diatomic(state):
    """ Get the vibrational quantum number for a diatomic in a dictionary. """
    qns = Qns.objects.filter(state=state)
    for qn in qns:
        if qn.qn_name == 'v':
            return {'v1': int(qn.qn_val)}
    return None

patt = 'v\d+$'
def get_vib_qns_polyatomic(state):
    """
    Return a dictionary of the vibrational quantum numbers for a polyatomic
    molecule.

    """
    qns = Qns.objects.filter(state=state)
    vib_qns = {}
    for qn in qns:
        qn_name = qn.qn_name
        if re.match(patt,qn_name):
            vib_qns[qn_name] = int(qn.qn_val)
    return vib_qns

# Decide what sort of molecule we're looking at, and assign the correct method
# for retrieving the vibrational quantum numbers from its states
diatomic = triatomic = polyatomic = False
# NB look only at the first iso, because the others must correspond to
# cases associated with the same number of atoms
if isos[0].case_id in (1,2,3):
    # diatomic cases: dcs, hunda, hundb have one vibrational
    # quantum number, "v"
    diatomic = True
    get_vib_qns = get_vib_qns_diatomic
elif isos[0].case_id in (4,5,12,14):
    # triatomic cases: ltcs, nltcs, ltos, nltos have three vibrational
    # quantum numbers, "v1", "v2", "v3"
    triatomic = True
    get_vib_qns = get_vib_qns_polyatomic
else:
    # molecules with more than three atoms have a potentially unlimited
    # number of quantum numbers: "vi", i=1,2,3,...; the ground state is
    # indicated by v1=v2=v3=v4=0
    polyatomic = True
    get_vib_qns = get_vib_qns_polyatomic

def get_s_v(v_qns):
    """
    Get a string corresponding to the vibrational state represented by
    the dictionary of vibrational quantum numbers, v_qns. e.g.
    {'v1': 1, 'v2': 2} --> 'v1+2v2'
    {'v1': 0, 'v2': 0, 'v3': 0} --> '0'
    """
    if not v_qns:
        return ''
    l_v = []
    for mode in sorted(v_qns.keys()):
        vi = v_qns[mode] 
        if  vi == 1:
            l_v.append(mode)
        elif vi > 1:
            l_v.append('%d%s' % (vi,mode))
    if not l_v:
        # ground state: all v's are 0
        return '0'
    return '+'.join(l_v)

# get all of the transitions for all of the isotopologues of our molecule
transitions = Trans.objects.filter(iso__in=isos)
ntrans = transitions.count()
print ntrans, 'transitions retrieved.'
i=0; last_pd = pd = 0
for transition in transitions:
    # progress indicator
    i += 1
    pd = int(float(i)/ntrans*100)
    if pd > last_pd:
        print pd,'%'
        last_pd = pd

    # get upper and lower vibrational state strings ...
    vp = get_vib_qns(transition.statep)
    s_vp = get_s_v(vp)
    vpp = get_vib_qns(transition.statepp)
    s_vpp = get_s_v(vpp)
    # ... and turn them into a band string:
    band = '%s-%s' % (s_vp, s_vpp)
    # update the transitions table with the band string
    command = 'UPDATE hitranlbl_trans set band="%s" where id=%d'\
        % (band, transition.id)
    cursor.execute(command)
    #print transition.id, ':', band
connection.commit()
    
