# -*- coding: utf-8 -*-
# hcase_hundb.py

# Christian Hill, 30/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_nltcs module, with methods for writing and parsing the quantum
# numbers of diatomic molecules described well by the Hund's case (b)
# coupling scheme from the HITRAN database.
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

    ElecStateLabelp = trans.Vp[7]
    if ElecStateLabelp == 'X':
        Sp = 1; Lambdap = 0 # X(3Sigma_g-) ground state
    elif ElecStateLabelp == 'a':
        Sp = 0; Lambdap = 2 # a(1Delta_g) excited state
    elif ElecStateLabelp == 'b':
        Sp = 0; Lambdap = 0 # b(1Sigma_g+) ground state
    else:
        # unknown electronic state
        Sp = Lambdap = None

    qnsp = {'ElecStateLabel': ElecStateLabelp, 'S': Sp, 'Lambda': Lambdap}
    # all transitions are from the X(3Sigma_g=) ground state:
    qnspp = {'ElecStateLabel': 'X', 'S': 1, 'Lambda': 0}

    save_qn(qnsp, 'v', trans.Vp[-2:])
    save_qn(qnspp, 'v', trans.Vpp[-2:])

    # rotational quantum numbers J and N are (non-negative) integers for
    # the states of O2 in HITRAN
    brJ = trans.Qpp[5]  # J-branch designation: 'P' or 'R'
    Jpp = save_qn(qnspp, 'J', trans.Qpp[6:9])
    if Jpp is not None and brJ:
        Jp = Jpp + branch[brJ]
        qnsp['J'] = Jp
    brN = trans.Qpp[1]  # N-branch designation
    Npp = save_qn(qnspp, 'N', trans.Qpp[2:5])
    if Npp is not None and brJ:
        Np = Npp + branch[brN]
        qnsp['N'] = Np

    # look for hyperfine quantum numbers, Fp and Fpp, which may be integer
    # or half-integer:
    save_qn(qnspp, 'F', trans.Qpp[9:14])
    save_qn(qnsp, 'F', trans.Qp[10:])

    multipole = 'E1'
    # for O2, the multipole designation, 'd', 'm' or 'q' is stored in Qpp[14]
    sympp = trans.Qpp[14]
    if sympp == 'q':    # electric quadrupole
        multipole = 'E2'
    elif sympp == 'm':  # magnetic dipole
        multipole = 'M1'

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

    Vp = '       %s     %s' % (ElecStateLabelp, s_vp)
    Vpp = '       %s     %s' % (ElecStateLabelpp, s_vpp)

    Jpp = trans.statepp_get('J')
    brJ = ' '
    s_Jpp = '   '
    if Jpp is not None:
        s_Jpp = '%3d' % Jpp
        Jp = trans.statep_get('J')
        if Jp is not None:
            brJ = branch.get(Jp - Jpp)
    Npp = trans.statepp_get('N')
    brN = ' '
    s_Npp = '   '
    if Npp is not None:
        s_Npp = '%3d' % Npp
        Np = trans.statep_get('N')
        if Np is not None:
            brN = branch.get(Np - Npp)

    s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5) 
    s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)

    # for O2, the Qpp[14] field holds a character identifying the transition
    # multipole ('d', 'q' or 'm'):
    sympp='d'
    if trans.multipole=='E2': sympp='q'    # electric quadrupole
    if trans.multipole=='M1': sympp='m'    # magnetic dipole

    Qpp = ' %s%s%s%s%s%s' % (brN, s_Npp, brJ, s_Jpp, s_Fpp, sympp)
    Qp = '          %s' % s_Fp
    
    return Vp, Vpp, Qp, Qpp
