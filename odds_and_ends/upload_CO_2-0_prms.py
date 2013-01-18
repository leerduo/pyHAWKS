# -*- coding: utf-8 -*-
# upload_CO_2-0_prms.py

import os
import sys
import math
import physcon as pc
import xn_utils

HOME = os.getenv('HOME')
PYHAWKS_PATH = os.path.join(HOME, 'research/HITRAN/pyHAWKS')
sys.path.append(PYHAWKS_PATH)
from hitran_param import HITRANParam
SETTINGS_PATH = os.path.join(HOME, 'research/VAMDC/HITRAN/django/HITRAN')
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection
from hitranmeta.models import Iso
from hitranlbl.models import State, Trans, Prm

cursor = connection.cursor()

c2 = pc.h * pc.c * 100. / pc.kB     # second radiation constant, cm.K
pic8 = 8. * math.pi * pc.c * 100    # 8.pi.c in cm-1 s
iso = Iso.objects.get(pk=26)    # (12C)(16O)
abundance = iso.abundance

branch = {'R': 1, 'P': -1}

HOME = os.getenv('HOME')
prm_filepath = os.path.join(HOME, 'research/HITRAN/HITRAN2008/updates')
prm_filename = os.path.join(prm_filepath, 'CO-121227/12CO-file.txt')

Q = 107.1134        # (12C)(16O) partition function at 296 K
T = 296.

def calc_A(nu, Epp, gp, Sw):
    """
    Calculate the Einstein A coefficient from the weighted line intensity, Sw

    """

    c2oT = c2 / T
    if Epp is None or gp is None:
        return None
    A = (Sw/abundance) * pic8 * nu**2 * Q / gp / math.exp(-c2oT * Epp)\
            / (1 - math.exp(-c2oT *nu))
    return A

with open(prm_filename, 'r') as fi:
    fi.readline()   # header
    for line in fi.readlines():
        if '===' in line:
            break
        branch_label = line[1]
        DeltaJ = branch[branch_label]
        Jpp = int(line[2:4])
        s_qnspp = 'ElecStateLabel=X;v=0;J=%d' % Jpp
        Jp = Jpp + DeltaJ
        s_qnsp = 'ElecStateLabel=X;v=2;J=%d' % Jp
        statespp = State.objects.filter(iso=iso).filter(s_qns=s_qnspp)
        statesp = State.objects.filter(iso=iso).filter(s_qns=s_qnsp)
        trans = Trans.objects.filter(iso=iso).filter(valid_to='3000-01-01')\
                    .filter(statep__in=statesp).filter(statepp__in=statespp)\
                    .get()
        trans_id = trans.id
        print trans_id, trans.nu, trans.statep.s_qns, '<-', trans.statepp.s_qns
        # parse the line from the 12CO-file.txt file
        nu = HITRANParam(xn_utils.str_to_num(line[4:17]), relative=False,
                         source_id=723)

        Sw = HITRANParam(xn_utils.str_to_num(line[23:32]), relative=False,
                         source_id=723)

        gamma_self = HITRANParam(xn_utils.str_to_num(line[36:43]),
                xn_utils.str_to_num(line[45:52]), relative=True, source_id=723)
        gamma_self.err = xn_utils.str_to_num(line[45:52])

        n_self = HITRANParam(xn_utils.str_to_num(line[52:59]),
                xn_utils.str_to_num(line[59:66]), relative=True, source_id=723)
        n_self.err = xn_utils.str_to_num(line[59:66])

        delta_self = HITRANParam(xn_utils.str_to_num(line[68:77]),
               xn_utils.str_to_num(line[80:89]), relative=False, source_id=723)

        deltap_self = HITRANParam(xn_utils.str_to_num(line[90:101]),
              xn_utils.str_to_num(line[103:114]), relative=True, source_id=723)
        deltap_self.err = xn_utils.str_to_num(line[103:114])

        SD = HITRANParam(xn_utils.str_to_num(line[117:125]),
              xn_utils.str_to_num(line[126:135]), relative=True, source_id=723)
        SD.err = xn_utils.str_to_num(line[126:135])

        gamma_air = HITRANParam(xn_utils.str_to_num(line[136:143]),
              xn_utils.str_to_num(line[145:153]), relative=True, source_id=723)
        gamma_air.err = xn_utils.str_to_num(line[145:153])

        n_air = HITRANParam(xn_utils.str_to_num(line[154:160]),
              xn_utils.str_to_num(line[161:168]), relative=True, source_id=723)
        n_air.err = xn_utils.str_to_num(line[161:168])

        delta_air = HITRANParam(xn_utils.str_to_num(line[169:178]),
             xn_utils.str_to_num(line[180:190]), relative=False, source_id=723)

        deltap_air = HITRANParam(xn_utils.str_to_num(line[191:202]),
             xn_utils.str_to_num(line[204:216]), relative=True, source_id=723)
        deltap_air.err = xn_utils.str_to_num(line[204:216])

        #new_trans = Trans(iso=trans.iso, statep=trans.statep,
        #                  statepp=trans.statepp, nu = nu.val, Sw = Sw.val,
        #                  A = calc_A(nu.val, trans.Elower, trans.gp, Sw.val),
        #                  multipole=trans.multipole, Elower=trans.Elower,
        #                  gp=trans.gp, gpp=trans.gpp,
        #                  valid_from='2013-01-07', valid_to='3000-01-01',
        #                  lineshape=1)
        #new_trans.pk = 0
        #new_trans.save()
        #print new_trans.pk

        #for prm_name in ('nu', 'Sw', 'gamma_self', 'n_self', 'delta_self',
        #                 'deltap_self', 'SD', 'gamma_air', 'n_air',
        #                 'delta_air', 'deltap_air'):
        for prm_name in ('n_self', 'delta_self', 'deltap_self', 'SD',
                         'deltap_air'):
            prm = globals()[prm_name]
            if prm.val is None:
                continue
            prm.set_ierr()
            print '%s = %s(%s){%s}[%d]' % (prm_name, str(prm.val),
                            str(prm.err), str(prm.ierr), prm.source_id)
            fields = ['trans_id', 'val']
            #vals = [str(new_trans.pk), str(prm.val)]
            vals = [str(trans_id), str(prm.val)]
            if prm.err is not None:
                fields.append('err')
                vals.append(str(prm.err))
                fields.append('ierr')
                vals.append(str(prm.ierr))
            fields.append('source_id')
            vals.append(str(prm.source_id))
            command = 'INSERT INTO prm_%s (%s) VALUES (%s)'\
                    % (prm_name.lower(), ', '.join(fields), ', '.join(vals))
            print command
            cursor.execute(command)
connection.commit()
