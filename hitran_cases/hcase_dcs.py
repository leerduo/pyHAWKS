# -*- coding: utf-8 -*-
# hcase_dcs.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_dcs module, with methods for writing and parsing the quantum
# numbers of closed-shell diatomic molecules in the HITRAN database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the closed-shell diatomic case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole indicates the nature of
    the transition ('E1' for electric dipole, 'M1' for magnetic dipole, and
    'E2' for electric quadrupole).

    """

    # in HITRAN, the only dcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    # vibrational quantum numbers are the only thing in the global
    # quanta field and they are always (non-negative) integers
    save_qn(qnsp, 'v', trans.Vp)
    save_qn(qnspp, 'v', trans.Vpp)

    # rotational quantum numbers are also (non-negative) integers for
    # closed-shell diatomic species:
    br = trans.Qpp[5]   # branch designation: 'P' or 'R'
    Jpp = save_qn(qnspp, 'J', trans.Qpp[6:9])
    if Jpp is not None and br:
        Jp = Jpp + branch[br]
        qnsp['J'] = Jp

    # look for hyperfine quantum numbers, Fp and Fpp, which may be integer
    # or half-integer:
    save_qn(qnspp, 'F', trans.Qpp[10:])
    save_qn(qnsp, 'F', trans.Qp[10:])

    multipole = 'E1'
    # for N2, sympp holds the multipole designation for the transition
    sympp = trans.Qpp[9]
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

    sympp=' '
    # for N2, the Sympp field holds a character identifying the transition
    # multipole:
    if trans.multipole=='E2': sympp='q'    # electric quadrupole
    if trans.multipole=='M1': sympp='m'    # magnetic dipole

    # 'global' quanta fields hold upper and lower state vibrational
    # quantum numbers:
    Vpp = qn_to_str(trans.statepp, 'v', '             %2d', ' '*15) 
    Vp = qn_to_str(trans.statep, 'v', '             %2d', ' '*15)

    # the only thing that could be in the Qp field is F'
    Qp = qn_to_str(trans.statep, 'F', '          %5.1f', ' '*15) 
    s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)

    Jpp = trans.statepp_get('J')
    br = ' '
    s_Jpp = '   '
    if Jpp is not None:
        s_Jpp = '%3d' % Jpp
        Jp = trans.statep_get('J')
        if Jp is not None:
            br = branch.get(Jp - Jpp)
    Qpp = '     %s%s%s%s' % (br, s_Jpp, sympp, s_Fpp)

    return Vp, Vpp, Qp, Qpp
