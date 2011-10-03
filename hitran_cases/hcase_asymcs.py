# -*- coding: utf-8 -*-
# hcase_asymcs.py

# Christian Hill, 6/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_asymcs module, with methods for writing and parsing the quantum
# numbers of closed-shell, asymmetric top molecules from the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the asymcs case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only asymcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    if trans.molec_id in (20, 25, 29):  # H2CO, H2O2, COF2
        save_qn(qnsp, 'v1', trans.Vp[3:5])
        save_qn(qnsp, 'v2', trans.Vp[5:7])
        save_qn(qnsp, 'v3', trans.Vp[7:9])
        save_qn(qnspp, 'v1', trans.Vpp[3:5])
        save_qn(qnspp, 'v2', trans.Vpp[5:7])
        save_qn(qnspp, 'v3', trans.Vpp[7:9])
        if trans.molec_id == 25:    # H2O2
            # torsional quantum labels instead of v4
            save_qn(qnsp, 'n', trans.Vp[9])
            save_qn(qnsp, 'tau', trans.Vp[10])
            save_qn(qnspp, 'n', trans.Vpp[9])
            save_qn(qnspp, 'tau', trans.Vpp[10])
        else:
            save_qn(qnsp, 'v4', trans.Vp[9:11])
            save_qn(qnspp, 'v4', trans.Vpp[9:11])
        save_qn(qnsp, 'v5', trans.Vp[11:13])
        save_qn(qnsp, 'v6', trans.Vp[13:15])
        save_qn(qnspp, 'v5', trans.Vpp[11:13])
        save_qn(qnspp, 'v6', trans.Vpp[13:15])
    else:
        for (mode, val) in get_normal_modes_V(trans.Vp):
             qnsp[mode] = val
        for (mode, val) in get_normal_modes_V(trans.Vpp):
             qnspp[mode] = val
    
    save_qn(qnsp, 'J', trans.Qp[:3])
    save_qn(qnsp, 'Ka', trans.Qp[3:6])
    save_qn(qnsp, 'Kc', trans.Qp[6:9])
    save_qn(qnsp, 'F', trans.Qp[9:14])

    save_qn(qnspp, 'J', trans.Qpp[:3])
    save_qn(qnspp, 'Ka', trans.Qpp[3:6])
    save_qn(qnspp, 'Kc', trans.Qpp[6:9])
    save_qn(qnspp, 'F', trans.Qpp[9:14])

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    ElecStateLabelp = qn_to_str(trans.statep, 'ElecStateLabel', '%1s', ' ')
    ElecStateLabelpp = qn_to_str(trans.statepp, 'ElecStateLabel', '%1s', ' ')

    if trans.molec_id in (20, 25, 29):  # H2CO, H2O2, COF2
        s_v1p = qn_to_str(trans.statep, 'v1', '%2d', '  ')
        s_v2p = qn_to_str(trans.statep, 'v2', '%2d', '  ')
        s_v3p = qn_to_str(trans.statep, 'v3', '%2d', '  ')
        s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
        s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
        s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
        s_v5p = qn_to_str(trans.statep, 'v5', '%2d', '  ')
        s_v6p = qn_to_str(trans.statep, 'v6', '%2d', '  ')
        s_v5pp = qn_to_str(trans.statepp, 'v5', '%2d', '  ')
        s_v6pp = qn_to_str(trans.statepp, 'v6', '%2d', '  ')
        if trans.molec_id == 25:   # H2O2
            s_np = qn_to_str(trans.statep, 'n', '%1d', ' ')
            s_taup = qn_to_str(trans.statep, 'tau', '%1d', ' ')
            s_npp = qn_to_str(trans.statepp, 'n', '%1d', ' ')
            s_taupp = qn_to_str(trans.statepp, 'tau', '%1d', ' ')
            Vp = '   %s%s%s%s%s%s%s' % (s_v1p, s_v2p, s_v3p, s_np, s_taup,
                                        s_v5p, s_v6p)
            Vpp = '   %s%s%s%s%s%s%s' % (s_v1pp, s_v2pp, s_v3pp, s_npp,
                                         s_taupp, s_v5pp, s_v6pp)
        else:
            s_v4p = qn_to_str(trans.statep, 'v4', '%2d', '  ')
            s_v4pp = qn_to_str(trans.statepp, 'v4', '%2d', '  ')
            Vp = '   %s%s%s%s%s%s' % (s_v1p, s_v2p, s_v3p, s_v4p, s_v5p, s_v6p)
            Vpp = '   %s%s%s%s%s%s' % (s_v1pp, s_v2pp, s_v3pp, s_v4pp,
                                       s_v5pp, s_v6pp)
    else:
        Vp = set_normal_modes_V(trans.statep)
        Vpp = set_normal_modes_V(trans.statepp)

    s_Jp = qn_to_str(trans.statep, 'J', '%3d', '   ')
    s_Kap = qn_to_str(trans.statep, 'Ka', '%3d', '   ')
    s_Kcp = qn_to_str(trans.statep, 'Kc', '%3d', '   ')
    s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5)

    s_Jpp = qn_to_str(trans.statepp, 'J', '%3d', '   ')
    s_Kapp = qn_to_str(trans.statepp, 'Ka', '%3d', '   ')
    s_Kcpp = qn_to_str(trans.statepp, 'Kc', '%3d', '   ')
    s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)

    Qp = '%s%s%s%s ' % (s_Jp, s_Kap, s_Kcp, s_Fp)
    Qpp = '%s%s%s%s ' % (s_Jpp, s_Kapp, s_Kcpp, s_Fpp)

    return Vp,Vpp,Qp,Qpp

