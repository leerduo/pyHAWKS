# -*- coding: utf-8 -*-
# hcase_pyrtet.py

# Christian Hill, 31/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_pyrtet module, with methods for writing and parsing the quantum
# numbers of closed-shell, pyramidal tetratomic molecules (a sort of symmetric
# top) from the HITRAN database: NH3 and PH3
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

    # in HITRAN, the only pyramidal tetratomic molecules are those in their
    # ground electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    save_qn(qnsp, 'v1', trans.Vp[5:7])
    save_qn(qnsp, 'v2', trans.Vp[7:9])
    save_qn(qnsp, 'v3', trans.Vp[9:11])
    save_qn(qnsp, 'v4', trans.Vp[11:13])
    save_qn(qnspp, 'v1', trans.Vpp[5:7])
    save_qn(qnspp, 'v2', trans.Vpp[7:9])
    save_qn(qnspp, 'v3', trans.Vpp[9:11])
    save_qn(qnspp, 'v4', trans.Vpp[11:13])
    if trans.molec_id == 11:    # vibrational inversion for NH3
        save_qn_str(qnsp, 'vibInv', trans.Vp[14])
        save_qn_str(qnspp, 'vibInv', trans.Vpp[14])
        # we only need vibrational symmetry for the upper state because
        # only excited levels such as 2v4 have more than one possible
        # symmetry and these don't serve as lower levels in HITRAN
        save_qn_str(qnsp, 'vibSym', trans.Vp[13])
    elif trans.molec_id == 28:  # PH3
        save_qn_str(qnsp, 'vibSym', trans.Qp[8:10])
        save_qn_str(qnspp, 'vibSym', trans.Qpp[8:10])

    save_qn(qnsp, 'J', trans.Qp[:3])
    save_qn(qnsp, 'K', trans.Qp[3:6])
    save_qn(qnsp, 'l', trans.Qp[6:8])

    save_qn(qnspp, 'J', trans.Qpp[:3])
    save_qn(qnspp, 'K', trans.Qpp[3:6])
    save_qn(qnspp, 'l', trans.Qpp[6:8])

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
    s_lp = qn_to_str(trans.statep, 'l', '%2d', '  ')
    s_Jp = qn_to_str(trans.statep, 'J', '%3d', '   ')
    s_Kp = qn_to_str(trans.statep, 'K', '%3d', '   ')
    s_vibinvp = qn_to_str(trans.statep, 'vibInv', '%1s', ' ')
    s_vibsymp = qn_to_str_ljust(trans.statep, 'vibSym', 2, '  ')
    
    s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
    s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
    s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
    s_v4pp = qn_to_str(trans.statepp, 'v4', '%2d', '  ')
    s_lpp = qn_to_str(trans.statepp, 'l', '%2d', '  ')
    s_Jpp = qn_to_str(trans.statepp, 'J', '%3d', '   ')
    s_Kpp = qn_to_str(trans.statepp, 'K', '%3d', '   ')
    s_vibinvpp = qn_to_str(trans.statepp, 'vibInv', '%1s', ' ')
    s_vibsympp = qn_to_str_ljust(trans.statepp, 'vibSym', 2, '  ')

    Vp  = '     %s%s%s%s %s' % (s_v1p, s_v2p, s_v3p, s_v4p, s_vibinvp)
    Vpp = '     %s%s%s%s %s' % (s_v1pp, s_v2pp, s_v3pp, s_v4pp, s_vibinvpp)

    if trans.molec_id == 11:    # NH3
        Qp  = '%s%s%s  %s    ' % (s_Jp, s_Kp, s_lp, s_vibinvp) 
        Qpp = '%s%s%s  %s    ' % (s_Jpp, s_Kpp, s_lpp, s_vibinvpp)
        # unassigned lower states don't quote the inversion symmetry,
        # even if it is known:
        sQpp = Qpp.strip()
        if sQpp in ('a', 's'):
            Qpp = ' '*15
    elif trans.molec_id == 28:  # PH3
        Qpp = '%s%s%s%s     ' % (s_Jpp, s_Kpp, s_lpp, s_vibsympp)
        Qp  = '%s%s%s%s     ' % (s_Jp, s_Kp, s_lp, s_vibsymp)

    return Vp,Vpp,Qp,Qpp
