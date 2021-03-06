# -*- coding: utf-8 -*-
# hcase_nltcs.py

# Christian Hill, 22/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_nltcs module, with methods for writing and parsing the quantum
# numbers of closed-shell non-linear triatomic molecules in the HITRAN
# database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the closed-shell non-linear triatomic case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only nltcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    if trans.molec_id == 3: # O3
        # vibrationally mixed states (for the upper state only)
        # are labelled with roman numerals
        roman_numeral_rank = trans.Vp[:9].strip()
        if roman_numeral_rank:
            if roman_numeral_rank == 'I':
                save_qn(qnsp, 'r', 1)
            elif roman_numeral_rank == 'II':
                save_qn(qnsp, 'r', 2)
            elif roman_numeral_rank == 'III':
                save_qn(qnsp, 'r', 3)
            else:
                raise ValueError('unidentified vibrational rank: %s'
                                 % roman_numeral_rank)

    save_qn(qnsp, 'v1', trans.Vp[9:11])
    save_qn(qnsp, 'v2', trans.Vp[11:13])
    save_qn(qnsp, 'v3', trans.Vp[13:15])
    save_qn(qnspp, 'v1', trans.Vpp[9:11])
    save_qn(qnspp, 'v2', trans.Vpp[11:13])
    save_qn(qnspp, 'v3', trans.Vpp[13:15])

    save_qn(qnsp, 'J', trans.Qp[0:3])
    save_qn(qnsp, 'Ka', trans.Qp[3:6])
    save_qn(qnsp, 'Kc', trans.Qp[6:9])
    save_qn(qnsp, 'F', trans.Qp[9:14])
    save_qn(qnspp, 'J', trans.Qpp[0:3])
    save_qn(qnspp, 'Ka', trans.Qpp[3:6])
    save_qn(qnspp, 'Kc', trans.Qpp[6:9])
    save_qn(qnspp, 'F', trans.Qpp[9:14])

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    # ranking index for vibrationally-mixed states
    s_rp = ' '*9
    r = trans.statep.get('r')
    if r:
        if r == 1:
            s_rp = '        I'
        elif r == 2:
            s_rp = '       II'
        elif r == 3:
            s_rp = '      III'

    s_v1p = qn_to_str(trans.statep, 'v1', '%2d', '  ')
    s_v2p = qn_to_str(trans.statep, 'v2', '%2d', '  ')
    s_v3p = qn_to_str(trans.statep, 'v3', '%2d', '  ')
    s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
    s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
    s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
    Vp = '%s%s%s%s' % (s_rp, s_v1p, s_v2p, s_v3p)
    Vpp = '         %s%s%s' % (s_v1pp, s_v2pp, s_v3pp)

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

    return Vp, Vpp, Qp, Qpp
