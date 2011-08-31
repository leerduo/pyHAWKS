# -*- coding: utf-8 -*-
# hcase_stcs.py

# Christian Hill, 31/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_stcs module, with methods for writing and parsing the quantum
# numbers of closed-shell, symmetric top molecules from the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the stcs case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only stcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}
    for (mode, val) in get_normal_modes_V(trans.Vp):
         qnsp[mode] = val
    for (mode, val) in get_normal_modes_V(trans.Vpp):
         qnspp[mode] = val
    
    save_qn(qnsp, 'J', trans.Qp[:3])
    save_qn(qnsp, 'K', trans.Qp[3:6])
    save_qn_str(qnsp, 'rovibSym', trans.Qp[8:10])
    save_qn(qnsp, 'F', trans.Qp[10:])

    save_qn(qnspp, 'J', trans.Qpp[:3])
    save_qn(qnspp, 'K', trans.Qpp[3:6])
    save_qn_str(qnspp, 'rovibSym', trans.Qpp[8:10])
    save_qn(qnspp, 'F', trans.Qpp[10:])

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    ElecStateLabelp = qn_to_str(trans.statep, 'ElecStateLabel', '%1s', ' ')
    ElecStateLabelpp = qn_to_str(trans.statepp, 'ElecStateLabel', '%1s', ' ')

    Vp = set_normal_modes_V(trans.statep)
    Vpp = set_normal_modes_V(trans.statepp)

    s_Jp = qn_to_str(trans.statep, 'J', '%3d', '   ')
    s_Kp = qn_to_str(trans.statep, 'K', '%3d', '   ')
    s_rovibsymp = qn_to_str_ljust(trans.statep, 'rovibSym', 2, '  ')
    s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5)

    s_Jpp = qn_to_str(trans.statepp, 'J', '%3d', '   ')
    s_Kpp = qn_to_str(trans.statepp, 'K', '%3d', '   ')
    s_rovibsympp = qn_to_str_ljust(trans.statepp, 'rovibSym', 2, '  ')
    s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)

    Qpp = '%s%s  %s%s' % (s_Jpp, s_Kpp, s_rovibsympp, s_Fpp)
    Qp = '%s%s  %s%s' % (s_Jp, s_Kp, s_rovibsymp, s_Fp)

    return Vp,Vpp,Qp,Qpp
