# -*- coding: utf-8 -*-
# upload_CO_SDV.py

import os
import sys

HOME = os.getenv('HOME')
HITRAN_PATH = '/Users/christian/research/HITRAN/HITRAN2008/updates'
SETTINGS_PATH = '/Users/christian/research/VAMDC/HITRAN/django/HITRAN'
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import connection
from hitranmeta.models import Iso
from hitranlbl.models import Trans
import xn_utils

branch = {'R': 1, 'P': -1, 1: 'R', -1: 'P'}

cursor = connection.cursor()

iso_ids = (26,27,28,29,30,31)
date = '2013-01-05'
SDV_filename = os.path.join(HITRAN_PATH,
                          'CO-121227/05_hit12_SDV.par')

isos = Iso.objects.filter(pk__in=iso_ids)
trans = Trans.objects.filter(iso__in=isos).filter(valid_from=date)\
                    .filter(band="2v1-0").order_by('nu')
print trans.count(),'transitions found'

lines = {}
with open(SDV_filename, 'r') as fi:
    fi.readline()   # throw away header    
    fi.readline()
    for line in fi.readlines():
        if line[17] != '2' or line[32] != '0':
            continue
        lines[line[:57]] = line

trans_dict = {}
for t in trans:
    vp = 2; vpp = 0
    Jpp = int(t.statepp.qns_set.get(qn_name='J').qn_val)
    Jp = int(t.statep.qns_set.get(qn_name='J').qn_val)
    vp = int(t.statep.qns_set.get(qn_name='v').qn_val)
    key = '%2d%1d              2              0                    '\
          '%1s%3d' % (t.iso.molecule_id, t.iso.isoID, branch[Jp-Jpp], Jpp)
    trans_dict[key] = t
    
for key, t in trans_dict.items():
    try:
        line = lines[key]
    except KeyError:
        print 'Missing transition from input file:\n%s' % key
        pass
        #sys.exit(1)

    vp = 2; vpp = 0
    Jpp = int(t.statepp.qns_set.get(qn_name='J').qn_val)
    Jp = int(t.statep.qns_set.get(qn_name='J').qn_val)
    vp = int(t.statep.qns_set.get(qn_name='v').qn_val)

    s_Wair = s_Yair = s_Wself = s_Yself = None
    try:
        s_Wair = xn_utils.str_to_num(line[91:99])
    except IndexError:
        pass
    try:
        s_Yair = xn_utils.str_to_num(line[99:107])
    except IndexError:
        pass
    try:
        s_Wself = xn_utils.str_to_num(line[116:124])
    except IndexError:
        pass
    try:
        s_Yself = xn_utils.str_to_num(line[124:132])
    except IndexError:
        pass

    print '%1d,%1s(%2d)' % (t.iso.isoID, branch[Jp-Jpp], Jpp),\
            s_Wair, s_Yair, s_Wself, s_Yself

    # upload Yair, Yself
    if s_Yself is not None:
        command = 'INSERT INTO prm_y_self (trans_id, val, source_id) VALUES'\
                  ' (%d, %f, 726)' % (t.id, float(s_Yself))
        print command
        cursor.execute(command)
    if s_Yair is not None:
        command = 'INSERT INTO prm_y_air (trans_id, val, source_id) VALUES'\
                  ' (%d, %f, 726)' % (t.id, float(s_Yair))
        print command
        cursor.execute(command)

    # find the transition for P(J"+1) or R(J"+1):
    keyp1 = '%2d%1d              2              0                    '\
          '%1s%3d' % (t.iso.molecule_id, t.iso.isoID, branch[Jp-Jpp], Jpp+1)
    try:
        tp1 = trans_dict[keyp1]
    except KeyError:
        print 'Missing tp1:\n%s' % keyp1
        continue

    if s_Wself is not None:
        command = 'INSERT INTO lc_w_self (trans_i_id, trans_j_id, val,'\
                  ' source_id) VALUES (%d, %d, %f, 719)' % (t.id, tp1.id,
                                                           float(s_Wself))
        print command
        cursor.execute(command)
    if s_Wair is not None:
        command = 'INSERT INTO lc_w_air (trans_i_id, trans_j_id, val,'\
                  ' source_id) VALUES (%d, %d, %f, 719)' % (t.id, tp1.id,
                                                           float(s_Wair))
        print command
        cursor.execute(command)
        
connection.commit()

