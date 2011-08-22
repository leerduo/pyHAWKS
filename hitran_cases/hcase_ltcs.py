# -*- coding: utf-8 -*-
# hcase_ltcs.py

# Christian Hill, 22/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_ltcs module, with methods for writing and parsing the quantum
# numbers of closed-shell linear triatomic molecules in the HITRAN
# database.
# Various things are imported from the hcase_globals module.

from hcase_globals import *

def parse_qns(trans):
    """
    Parse the quantum numbers for the upper and lower states of HITRAN
    transition trans for the closed-shell linear triatomic case.
    The returned values are qnsp, qnspp, multiple, where qnsp and qnspp
    are dictionaries of upper and lower state quantum numbers respectively,
    keyed by quantum number name, and multipole = 'E1' (all the transitions
    for these molecules in HITRAN are electric dipole induced).

    """

    # in HITRAN, the only ltcs molecules are those in their ground
    # electronic states:
    qnsp = {'ElecStateLabel': 'X'}
    qnspp = {'ElecStateLabel': 'X'}

    # vibrational quantum numbers
    if trans.molec_id == 2: # CO2
        save_qn(qnsp, 'v1', trans.Vp[6:8])
        save_qn(qnsp, 'v2', trans.Vp[8:10])
        save_qn(qnsp, 'l2', trans.Vp[10:12])
        save_qn(qnsp, 'v3', trans.Vp[12:14])
        save_qn(qnsp, 'r', trans.Vp[14])

        save_qn(qnspp, 'v1', trans.Vpp[6:8])
        save_qn(qnspp, 'v2', trans.Vpp[8:10])
        save_qn(qnspp, 'l2', trans.Vpp[10:12])
        save_qn(qnspp, 'v3', trans.Vpp[12:14])
        save_qn(qnspp, 'r', trans.Vpp[14])
    else:   # N2O, OCS, HCN
        save_qn(qnsp, 'v1', trans.Vp[7:9])
        save_qn(qnsp, 'v2', trans.Vp[9:11])
        save_qn(qnsp, 'l2', trans.Vp[11:13])
        save_qn(qnsp, 'v3', trans.Vp[13:15])

        save_qn(qnspp, 'v1', trans.Vpp[7:9])
        save_qn(qnspp, 'v2', trans.Vpp[9:11])
        save_qn(qnspp, 'l2', trans.Vpp[11:13])
        save_qn(qnspp, 'v3', trans.Vpp[13:15])

    # rotational quantum number, J
    br = trans.Qpp[5]   # branch designation: 'P' or 'R'
    Jpp = save_qn(qnspp, 'J', trans.Qpp[6:9])
    if Jpp is not None and br:
        Jp = Jpp + branch[br]
        qnsp['J'] = Jp

    # Kronig (rotationless) parity, 'e' or 'f'
    kronig_paritypp = trans.Qpp[9]
    if kronig_paritypp != ' ':
        qnspp['kronigParity'] = kronig_paritypp
        # the only transitions in the database are e->e and f->f
        qnsp['kronigParity'] = kronig_paritypp

    # look for hyperfine quantum numbers, Fp and Fpp, which may be integer
    # or half-integer:
    save_qn(qnspp, 'F', trans.Qpp[10:])
    save_qn(qnsp, 'F', trans.Qp[10:])

    return qnsp, qnspp, 'E1'

def get_hitran_quanta(trans):
    """
    Write and return the Vp, Vpp, Qp, Qpp strings for global and local
    quanta in HITRAN2004+ format.

    """

    s_v1p = qn_to_str(trans.statep, 'v1', '%2d', '  ')
    s_v2p = qn_to_str(trans.statep, 'v2', '%2d', '  ')
    s_l2p = qn_to_str(trans.statep, 'l2', '%2d', '  ')
    s_v3p = qn_to_str(trans.statep, 'v3', '%2d', '  ')
    if trans.molec_id == 2: # CO2
        s_rp = qn_to_str(trans.statep, 'r', '%1d', ' ')
        Vp = '      %s%s%s%s%s' % (s_v1p, s_v2p, s_l2p, s_v3p, s_rp)
    else:
        Vp = '       %s%s%s%s' % (s_v1p, s_v2p, s_l2p, s_v3p)

    s_v1pp = qn_to_str(trans.statepp, 'v1', '%2d', '  ')
    s_v2pp = qn_to_str(trans.statepp, 'v2', '%2d', '  ')
    s_l2pp = qn_to_str(trans.statepp, 'l2', '%2d', '  ')
    s_v3pp = qn_to_str(trans.statepp, 'v3', '%2d', '  ')
    if trans.molec_id == 2: # CO2
        s_rpp = qn_to_str(trans.statepp, 'r', '%1d', ' ')
        Vpp = '      %s%s%s%s%s' % (s_v1pp, s_v2pp, s_l2pp, s_v3pp, s_rpp)
    else:
        Vpp = '       %s%s%s%s' % (s_v1pp, s_v2pp, s_l2pp, s_v3pp)
       
    Jpp = trans.statepp_get('J')
    br = ' '
    s_Jpp = '   '
    if Jpp is not None:
        s_Jpp = '%3d' % Jpp
        Jp = trans.statep_get('J')
        if Jp is not None:
            br = branch.get(Jp - Jpp)

    # Kronig (rotationless) parity, 'e' or 'f'
    kronig_paritypp = trans.statepp_get('kronigParity', ' ')

    if trans.molec_id == 23:    # HCN
        # 14N has integer spin, so F is an integer
        s_Fp = qn_to_str(trans.statep, 'F', '%5d', ' '*5)
        s_Fpp = qn_to_str(trans.statepp, 'F', '%5d', ' '*5)
    else:
        # the other nuclei giving rise to hyperfine coupling have
        # half-(odd)-integer spin, so F is half-(odd)-integer
        s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5)
        s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)

    Qpp = '     %s%s%s%s' % (br, s_Jpp, kronig_paritypp, s_Fpp)
    Qp = '          %s' % s_Fp

    return Vp, Vpp, Qp, Qpp
