# -*- coding: utf-8 -*-
# hcase_sphcs.py

# Christian Hill, 31/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_sphcs module, with methods for writing and parsing the quantum
# numbers of closed-shell, spherical top molecules from the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the sphcs case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only sphcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    save_qn(qnsp, 'v1', trans.Vp[3:5])
    save_qn(qnsp, 'v2', trans.Vp[5:7])
    save_qn(qnsp, 'v3', trans.Vp[7:9])
    save_qn(qnsp, 'v4', trans.Vp[9:11])
    save_qn(qnsp, 'n', trans.Vp[11:13])
    save_qn(qnsp, 'vibSym', trans.Vp[13:15])

    save_qn(qnspp, 'v1', trans.Vpp[3:5])
    save_qn(qnspp, 'v2', trans.Vpp[5:7])
    save_qn(qnspp, 'v3', trans.Vpp[7:9])
    save_qn(qnspp, 'v4', trans.Vpp[9:11])
    save_qn(qnspp, 'n', trans.Vpp[11:13])
    save_qn(qnspp, 'vibSym', trans.Vpp[13:15])

    save_qn(qnsp, 'J', trans.Qp[2:5])
    save_qn(qnsp, 'rovibSym', trans.Qp[5:7])
    save_qn(qnsp, 'alpha', trans.Qp[7:10])
    save_qn(qnsp, 'F', trans.Qp[10:15])

    save_qn(qnspp, 'J', trans.Qpp[2:5])
    save_qn(qnspp, 'rovibSym', trans.Qpp[5:7])
    save_qn(qnspp, 'alpha', trans.Qpp[7:10])
    save_qn(qnspp, 'F', trans.Qpp[10:15])

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    ElecStateLabelp = qn_to_str(trans.statep, 'ElecStateLabel', '%1s', ' ')
    ElecStateLabelpp = qn_to_str(trans.statepp, 'ElecStateLabel', '%1s', ' ')

    s_v1p = qn_to_str(trans.statep, 'v1', '%2d', '  ')
    s_v2p = qn_to_str(trans.statep, 'v2', '%2d', '  ')
    s_v3p = qn_to_str(trans.statep, 'v3', '%2d', '  ')
    s_v4p = qn_to_str(trans.statep, 'v4', '%2d', '  ')
    s_np = qn_to_str(trans.statep, 'n', '%2d', '  ')
    s_vibsymp = qn_to_str(trans.statep, 'vibSym', '%2s', '  ')
    
    s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
    s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
    s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
    s_v4pp = qn_to_str(trans.statepp, 'v4', '%2d', '  ')
    s_npp = qn_to_str(trans.statepp, 'n', '%2d', '  ')
    s_vibsympp = qn_to_str(trans.statepp, 'vibSym', '%2s', '  ')

    Vp = '   %s%s%s%s%s%s' % (s_v1p, s_v2p, s_v3p, s_v4p, s_np, s_vibsymp)
    Vpp = '   %s%s%s%s%s%s'%(s_v1pp, s_v2pp, s_v3pp, s_v4pp, s_npp, s_vibsympp)

    s_Jp = qn_to_str(trans.statep, 'J', '%3d', '   ')
    s_rovibsymp = qn_to_str(trans.statep, 'rovibSym', '%2s', '  ')
    s_alphap = qn_to_str(trans.statep, 'alpha', '%3d', '   ')
    # for methane-h4, the only hyperfine coupling is with (13C) for which
    # I=1 and therefore, F is an integer
    s_Fp = qn_to_str(trans.statep, 'F', '%3d', ' '*5)

    s_Jpp = qn_to_str(trans.statepp, 'J', '%3d', '   ')
    s_rovibsympp = qn_to_str(trans.statepp, 'rovibSym', '%2s', '  ')
    s_alphapp = qn_to_str(trans.statepp, 'alpha', '%3d', '   ')
    # for methane-h4, the only hyperfine coupling is with (13C) for which
    # I=1 and therefore, F is an integer
    s_Fpp = qn_to_str(trans.statepp, 'F', '%3d', ' '*5)

    Qp = '  %s%s%s%s' % (s_Jp, s_rovibsymp, s_alphap, s_Fp)
    Qpp = '  %s%s%s%s' % (s_Jpp, s_rovibsympp, s_alphapp, s_Fpp)

    return Vp,Vpp,Qp,Qpp

