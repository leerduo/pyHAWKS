# -*- coding: utf-8 -*-
# hcase_lpcs.py

# Christian Hill, 18/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_lpcs module, with methods for writing and parsing the quantum
# numbers of closed-shell, linear molecules from the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the lpcs case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only asymcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    if trans.molec_id == 26:    # C2H2
        save_qn(qnsp, 'v1', trans.Vp[0:2])
        save_qn(qnsp, 'v2', trans.Vp[2:4])
        save_qn(qnsp, 'v3', trans.Vp[4:6])
        save_qn(qnsp, 'v4', trans.Vp[6:8])
        save_qn(qnsp, 'v5', trans.Vp[8:10])
        save_qn(qnsp, 'l', trans.Vp[10:12])
        save_qn_str(qnsp, 'vibRefl', trans.Vp[12])
        save_qn(qnsp, 'r', trans.Vp[13])
        save_qn_str(qnsp, 'vibInv', trans.Vp[14])

        save_qn(qnspp, 'v1', trans.Vpp[0:2])
        save_qn(qnspp, 'v2', trans.Vpp[2:4])
        save_qn(qnspp, 'v3', trans.Vpp[4:6])
        save_qn(qnspp, 'v4', trans.Vpp[6:8])
        save_qn(qnspp, 'v5', trans.Vpp[8:10])
        save_qn(qnspp, 'l', trans.Vpp[10:12])
        save_qn_str(qnspp, 'vibRefl', trans.Vpp[12])
        save_qn(qnspp, 'r', trans.Vpp[13])
        save_qn_str(qnspp, 'vibInv', trans.Vpp[14])
    if trans.molec_id == 44:    # HC3N
        save_qn(qnsp, 'v1', trans.Vp[2])
        save_qn(qnsp, 'v2', trans.Vp[3])
        save_qn(qnsp, 'v3', trans.Vp[4])
        save_qn(qnsp, 'v4', trans.Vp[5])
        save_qn(qnsp, 'v5', trans.Vp[6])
        save_qn(qnsp, 'v6', trans.Vp[7])
        save_qn(qnsp, 'v7', trans.Vp[8])
        save_qn(qnsp, 'l5', trans.Vp[9:11])
        save_qn(qnsp, 'l6', trans.Vp[11:13])
        save_qn(qnsp, 'l7', trans.Vp[13:15])
        save_qn(qnspp, 'v1', trans.Vpp[2])
        save_qn(qnspp, 'v2', trans.Vpp[3])
        save_qn(qnspp, 'v3', trans.Vpp[4])
        save_qn(qnspp, 'v4', trans.Vpp[5])
        save_qn(qnspp, 'v5', trans.Vpp[6])
        save_qn(qnspp, 'v6', trans.Vpp[7])
        save_qn(qnspp, 'v7', trans.Vpp[8])
        save_qn(qnspp, 'l5', trans.Vpp[9:11])
        save_qn(qnspp, 'l6', trans.Vpp[11:13])
        save_qn(qnspp, 'l7', trans.Vpp[13:15])

    Jpp = save_qn(qnspp, 'J', trans.Qpp[6:9])
    br = trans.Qpp[5]   # branch designation: 'P' or 'R'
    Jp = None
    if Jpp is not None and br:
        Jp = Jpp + branch[br]
        qnsp['J'] = Jp

    kronig_paritypp = save_qn_str(qnspp, 'kronigParity', trans.Qpp[9])
    paritypp = xn_utils.kp_to_par(kronig_paritypp, Jpp)
    save_qn_str(qnspp, 'parity', paritypp)
    # electric dipole transitions are '+' <-> '-'
    parityp = xn_utils.other_par(paritypp)
    save_qn_str(qnsp, 'parity', parityp)
    if parityp is not None and Jp is not None:
        kronig_parityp = xn_utils.par_to_kp(parityp, Jp)
        save_qn_str(qnsp, 'kronigParity', kronig_parityp)

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    ElecStateLabelp = qn_to_str(trans.statep, 'ElecStateLabel', '%1s', ' ')
    ElecStateLabelpp = qn_to_str(trans.statepp, 'ElecStateLabel', '%1s', ' ')

    if trans.molec_id == 26:    # C2H2
        s_v1p = qn_to_str(trans.statep, 'v1', '%2d', '  ')
        s_v2p = qn_to_str(trans.statep, 'v2', '%2d', '  ')
        s_v3p = qn_to_str(trans.statep, 'v3', '%2d', '  ')
        s_v4p = qn_to_str(trans.statep, 'v4', '%2d', '  ')
        s_v5p = qn_to_str(trans.statep, 'v5', '%2d', '  ')
        s_lp = qn_to_str(trans.statep, 'l', '%2d', '  ')
        vib_reflp = qn_to_str(trans.statep, 'vibRefl', '%s', ' ')
        s_rp = qn_to_str(trans.statep, 'r', '%1d', ' ')
        vib_invp = qn_to_str(trans.statep, 'vibInv', '%s', ' ')
        
        s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
        s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
        s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
        s_v4pp = qn_to_str(trans.statepp, 'v4', '%2d', '  ')
        s_v5pp = qn_to_str(trans.statepp, 'v5', '%2d', '  ')
        s_lpp = qn_to_str(trans.statepp, 'l', '%2d', '  ')
        vib_reflpp = qn_to_str(trans.statepp, 'vibRefl', '%s', ' ')
        s_rpp = qn_to_str(trans.statepp, 'r', '%1d', ' ')
        vib_invpp = qn_to_str(trans.statepp, 'vibInv', '%s', ' ')
        Vp = '%s%s%s%s%s%s%s%s%s' % (s_v1p, s_v2p, s_v3p, s_v4p, s_v5p,
                                    s_lp, vib_reflp, s_rp, vib_invp)
        Vpp = '%s%s%s%s%s%s%s%s%s' % (s_v1pp, s_v2pp, s_v3pp, s_v4pp, s_v5pp,
                                     s_lpp, vib_reflpp, s_rpp, vib_invpp)

    if trans.molec_id == 44:    # HC3N
        s_v1p = qn_to_str(trans.statep, 'v1', '%1d', ' ')
        s_v2p = qn_to_str(trans.statep, 'v2', '%1d', ' ')
        s_v3p = qn_to_str(trans.statep, 'v3', '%1d', ' ')
        s_v4p = qn_to_str(trans.statep, 'v4', '%1d', ' ')
        s_v5p = qn_to_str(trans.statep, 'v5', '%1d', ' ')
        s_v6p = qn_to_str(trans.statep, 'v6', '%1d', ' ')
        s_v7p = qn_to_str(trans.statep, 'v7', '%1d', ' ')
        s_l5p = qn_to_str(trans.statep, 'l5', '%2d', '  ')
        s_l6p = qn_to_str(trans.statep, 'l6', '%2d', '  ')
        s_l7p = qn_to_str(trans.statep, 'l7', '%2d', '  ')
        s_v1pp = qn_to_str(trans.statepp, 'v1', '%1d', ' ')
        s_v2pp = qn_to_str(trans.statepp, 'v2', '%1d', ' ')
        s_v3pp = qn_to_str(trans.statepp, 'v3', '%1d', ' ')
        s_v4pp = qn_to_str(trans.statepp, 'v4', '%1d', ' ')
        s_v5pp = qn_to_str(trans.statepp, 'v5', '%1d', ' ')
        s_v6pp = qn_to_str(trans.statepp, 'v6', '%1d', ' ')
        s_v7pp = qn_to_str(trans.statepp, 'v7', '%1d', ' ')
        s_l5pp = qn_to_str(trans.statepp, 'l5', '%2d', '  ')
        s_l6pp = qn_to_str(trans.statepp, 'l6', '%2d', '  ')
        s_l7pp = qn_to_str(trans.statepp, 'l7', '%2d', '  ')
        Vp = '  %s%s%s%s%s%s%s%s%s%s' % (s_v1p, s_v2p, s_v3p, s_v4p, s_v5p,
                                         s_v6p, s_v7p, s_l5p, s_l6p, s_l7p)
        Vpp = '  %s%s%s%s%s%s%s%s%s%s' % (s_v1pp, s_v2pp, s_v3pp, s_v4pp,
                                s_v5pp, s_v6pp, s_v7pp, s_l5pp, s_l6pp, s_l7pp)

    Jpp = trans.statepp_get('J')
    br = ' '
    s_Jpp = '   '
    if Jpp is not None:
        s_Jpp = '%3d' % Jpp
        Jp = trans.statep_get('J')
        if Jp is not None:
            br = branch.get(Jp - Jpp)
    kronig_paritypp = qn_to_str(trans.statepp, 'kronigParity', '%s', ' ')

    Qpp = '     %s%s%s     ' % (br, s_Jpp, kronig_paritypp)
    Qp = ' '*15

    return Vp, Vpp, Qp, Qpp

