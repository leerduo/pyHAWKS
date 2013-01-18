# -*- coding: utf-8 -*-
# hcase_OHAX.py

# Christian Hill, 19/12/12
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_OHAX module, with methods for writing and parsing the quantum
# numbers of the OH A-X system, in which the upper A(2Sigma+) state is
# described by Hund's case (b) and the lower X(2Pi_i) state is described
# by Hund's case (a), from the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the hundb case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1', 'E2', or 'M1' for
    electric dipole, electric quadrupole, or magnetic dipole transitions
    respectively.

    """

    # OH (A-X) system
    multipole = 'E1'
    ElecStateLabelp = 'A'; ElecStateLabelpp = 'X'
    qnsp = {'ElecStateLabel': ElecStateLabelp, 'S': 0.5, 'Lambda': 0}
    qnspp = {'ElecStateLabel': ElecStateLabelpp, 'S': 0.5, 'Lambda': 1}

    SpinComponentLabelp = int(trans.Vp[8])  # 1 or 2
    if SpinComponentLabelp == 1:
        kronig_parityp = 'e'
    elif SpinComponentLabelp == 2:
        kronig_parityp = 'f'
    save_qn(qnsp, 'v', trans.Vp[-2:])
    qnsp['SpinComponentLabel'] = SpinComponentLabelp
    qnsp['kronigParity'] = kronig_parityp

    elec_strpp = trans.Vpp[8:11]
    if elec_strpp == '3/2':
        Omegapp = qnspp['Omega'] = 1.5
    elif elec_strpp == '1/2':
        Omegapp = qnspp['Omega'] = 0.5
    save_qn(qnspp, 'v', trans.Vpp[-2:])

    brN = trans.Qpp[2]
    brJ = trans.Qpp[3]

    Jpp = save_qn(qnspp, 'J', trans.Qpp[4:9])
    Jp = qnsp['J'] = Jpp + branch[brJ]
    if SpinComponentLabelp == 1:
        Np = int(Jp - 0.5)
    elif SpinComponentLabelp == 2:
        Np = int(Jp + 0.5)
    qnsp['N'] = Np
    kronig_paritypp = save_qn_str(qnspp, 'kronigParity', trans.Qpp[9])
    parityp = xn_utils.kp_to_par(kronig_parityp, Jp)
    save_qn_str(qnsp, 'parity', parityp)
    paritypp = xn_utils.kp_to_par(kronig_paritypp, Jpp)
    save_qn_str(qnspp, 'parity', paritypp)

    # sanity check:
    if parityp != xn_utils.other_par(paritypp):
        print 'bad parity in line:\n', trans.par_line

    return qnsp, qnspp, multipole

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    ElecStateLabelp = qn_to_str(trans.statep, 'ElecStateLabel', '%1s', ' ')
    ElecStateLabelpp = qn_to_str(trans.statepp, 'ElecStateLabel', '%1s', ' ')
    s_vp = qn_to_str(trans.statep, 'v', '%2d', '  ')
    s_vpp = qn_to_str(trans.statepp, 'v', '%2d', '  ')
    s_omegapp = qn_to_frac(trans.statepp, 'Omega', '   ')
    s_SpinComponentLabelp = qn_to_str(trans.statep, 'SpinComponentLabel',
                                      '%1s', ' ')

    Vp = '       %s%s    %s' % (ElecStateLabelp, s_SpinComponentLabelp, s_vp)
    Vpp = '       %s%s  %s' % (ElecStateLabelpp, s_omegapp, s_vpp)

    Jpp = trans.statepp_get('J')
    brJ = ' '
    s_Jpp = '   '
    if Jpp is not None:
        s_Jpp = '%5.1f' % Jpp
        Jp = trans.statep_get('J')
        if Jp is not None:
            brJ = branch.get(Jp - Jpp)
    # XXX N is not stored for case hunda, so we can't deduce brN
    brN = ' '
    kronig_paritypp = qn_to_str(trans.statepp, 'kronigParity', '%s', ' ')

    s_multipole = 'E1'
    Qpp = '  %s%s%s%s     ' % (brN, brJ, s_Jpp, kronig_paritypp)
    Qp = ' '*15
    
    return Vp, Vpp, Qp, Qpp

