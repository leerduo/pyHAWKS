# -*- coding: utf-8 -*-
# hcase_nltos.py

# Christian Hill, 11/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_nltos module, with methods for writing and parsing the quantum
# numbers of open-shell non-linear triatomic molecules in the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the open-shell non-linear triatomic case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only nltos molecules are those in their ground
    # doublet electronic states:
    qnsp = {'ElecStateLabel': 'X', 'S': 0.5}
    qnspp = {'ElecStateLabel': 'X', 'S': 0.5}

    save_qn(qnsp, 'v1', trans.Vp[9:11])
    save_qn(qnsp, 'v2', trans.Vp[11:13])
    save_qn(qnsp, 'v3', trans.Vp[13:15])
    save_qn(qnspp, 'v1', trans.Vpp[9:11])
    save_qn(qnspp, 'v2', trans.Vpp[11:13])
    save_qn(qnspp, 'v3', trans.Vpp[13:15])

    save_qn(qnsp, 'N', trans.Qp[0:3])
    save_qn(qnsp, 'Ka', trans.Qp[3:6])
    save_qn(qnsp, 'Kc', trans.Qp[6:9])
    save_qn(qnsp, 'F', trans.Qp[9:14])
    save_qn(qnspp, 'N', trans.Qpp[0:3])
    save_qn(qnspp, 'Ka', trans.Qpp[3:6])
    save_qn(qnspp, 'Kc', trans.Qpp[6:9])
    save_qn(qnspp, 'F', trans.Qpp[9:14])

    # the character '+' or '-' in Q[14] indicates J = N + 0.5 or J = N - 0.5
    sp = None
    if trans.Qp[14] == '+':
        sp = 1
    elif trans.Qp[14] == '-':
        sp = -1
    try:
        qnsp['J'] = qnsp['N'] + sp * 0.5
    except (TypeError, KeyError):   # no sp or no N
        pass
    spp = None
    if trans.Qpp[14] == '+':
        spp = 1
    elif trans.Qpp[14] == '-':
        spp = -1
    try:
        qnspp['J'] = qnspp['N'] + spp * 0.5
    except (TypeError, KeyError):   # no spp or no N
        pass

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    s_v1p = qn_to_str(trans.statep, 'v1', '%2d', '  ')
    s_v2p = qn_to_str(trans.statep, 'v2', '%2d', '  ')
    s_v3p = qn_to_str(trans.statep, 'v3', '%2d', '  ')
    s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
    s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
    s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
    Vp = '         %s%s%s' % (s_v1p, s_v2p, s_v3p)
    Vpp = '         %s%s%s' % (s_v1pp, s_v2pp, s_v3pp)

    s_Np = qn_to_str(trans.statep, 'N', '%3d', '   ')
    s_Kap = qn_to_str(trans.statep, 'Ka', '%3d', '   ')
    s_Kcp = qn_to_str(trans.statep, 'Kc', '%3d', '   ')

    s_Npp = qn_to_str(trans.statepp, 'N', '%3d', '   ')
    s_Kapp = qn_to_str(trans.statepp, 'Ka', '%3d', '   ')
    s_Kcpp = qn_to_str(trans.statepp, 'Kc', '%3d', '   ')

    if trans.molec_id == 10:    # NO2 (half-integer F)
        s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5)
        s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)
    elif trans.molec_id == 33:  # HO2 (integer F)
        s_Fp = qn_to_str(trans.statep, 'F', '%5d', ' '*5)
        s_Fpp = qn_to_str(trans.statepp, 'F', '%5d', ' '*5)

    symp = ' '
    Jp = trans.statep_get('J')
    Np = trans.statep_get('N')
    if Jp is not None and Np is not None:
        if Jp < Np:
            symp = '-'
        elif Jp > Np:
            symp = '+'
    sympp = ' '
    Jpp = trans.statepp_get('J')
    Npp = trans.statepp_get('N')
    if Jpp is not None and Npp is not None:
        if Jpp < Npp:
            sympp = '-'
        elif Jpp > Npp:
            sympp = '+'

    Qp = '%s%s%s%s%s' % (s_Np, s_Kap, s_Kcp, s_Fp, symp)
    Qpp = '%s%s%s%s%s' % (s_Npp, s_Kapp, s_Kcpp, s_Fpp, sympp)

    return Vp, Vpp, Qp, Qpp
