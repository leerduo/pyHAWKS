# -*- coding: utf-8 -*-
# hcase_hunda.py

# Christian Hill, 17/9/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_hunda module, with methods for writing and parsing the quantum
# numbers of diatomic molecules described well by the Hund's case (a)
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

    # in HITRAN, the only Hund's case (a) molecules are 2Pi molecules
    # in their ground electronic states:
    ElecStateLabelp = 'X'; ElecStateLabelpp = 'X'
    qnsp = {'ElecStateLabel': ElecStateLabelp, 'S': 0.5, 'Lambda': 1}
    qnspp = {'ElecStateLabel': ElecStateLabelpp, 'S': 0.5, 'Lambda': 1}

    Omegap = None
    elec_strp = trans.Vp[8:11]
    if elec_strp == '3/2':
        Omegap = qnsp['Omega'] = 1.5
    elif elec_strp == '1/2':
        Omegap = qnsp['Omega'] = 0.5
    elec_strpp = trans.Vpp[8:11]
    if elec_strpp == '3/2':
        Omegapp = qnspp['Omega'] = 1.5
    elif elec_strpp == '1/2':
        Omegapp = qnspp['Omega'] = 0.5

    save_qn(qnsp, 'v', trans.Vp[-2:])
    save_qn(qnspp, 'v', trans.Vpp[-2:])

    multipole = 'E1'
    reg = 1 # regular spin-orbit splitting
    if trans.molec_id == 13:    # OH
        reg = -1    # inverted spin-orbit splitting
        # OH has its own format for the Qpp field
        brN = trans.Qpp[1]
        brJ = trans.Qpp[2]
        Jpp = save_qn(qnspp, 'J', trans.Qpp[3:8])
        if Jpp is not None and brJ:
            Jp = qnsp['J'] = Jpp + branch[brJ]
        # upper and lower Lambda-doubling symmtries are given in Qpp
        kronig_parityp = save_qn_str(qnsp, 'kronigParity', trans.Qpp[8])
        save_qn_str(qnsp, 'parity', xn_utils.kp_to_par(kronig_parityp, Jp))
        kronig_paritypp = save_qn_str(qnspp, 'kronigParity', trans.Qpp[9])
        save_qn_str(qnspp, 'parity', xn_utils.kp_to_par(kronig_paritypp, Jpp)) 
    else:   # NO, ClO
        brN = trans.Qpp[2]
        brJ = trans.Qpp[3]
        Jpp = save_qn(qnspp, 'J', trans.Qpp[4:9])
        kronig_paritypp = save_qn_str(qnspp, 'kronigParity', trans.Qpp[9])
        paritypp = xn_utils.kp_to_par(kronig_paritypp, Jpp)
        save_qn_str(qnspp, 'parity', paritypp)
        if trans.Qp[0] == 'm':
            # magnetic dipole transitions are '-' <-> '-' and '+' <-> '+'
            multipole = 'M1'
            parityp = paritypp
        else:
            # electric dipole transitions are '+' <-> '-'
            parityp = xn_utils.other_par(paritypp)
        if Jpp is not None and brJ:
            Jp = qnsp['J'] = Jpp + branch[brJ]
        # deduce and save Kronig parity
        kronig_parityp = xn_utils.par_to_kp(parityp, Jp)
        save_qn_str(qnsp, 'parity', parityp)
        save_qn_str(qnsp, 'kronigParity', kronig_parityp)
    save_qn(qnspp, 'F', trans.Qpp[10:])
    save_qn(qnsp, 'F', trans.Qp[10:])

    # now try to deduce N', N" - XXX NB these are not stored for case hunda!
    # regular spin-orbit splitting:
    # Omega = 0.5 => J = N + 1/2, Omega = 1.5 => J = N - 1/2
    # NB this is wrong for NO in the HITRAN 2004 paper (p.175)
    # (opposite way round for inverted spin-orbit splitting)
    if Omegapp is not None:
        if Omegapp < 1.:
            Npp = int(Jpp - reg * 0.5)
            # NB for J = 1/2, Omega = 1/2, N must be 1
            if Npp == 0:
                Npp = 1
        else:
            Npp = int(Jpp + reg * 0.5)
        qnspp['N'] = Npp
    # This is the way I want to do it:
    if Omegap is not None:
        if Omegap < 1.:
            Np = int(Jp - reg * 0.5)
            # NB for J = 1/2, Omega = 1/2, N must be 1
            if Np==0:
                Np = 1
        else:
            Np = int(Jp + reg * 0.5)
        qnsp['N'] = Np
    # sanity check:
    #if brN and branch[Np-Npp] != brN:
    #    print 'invalid branch specification:', brN, ' for DeltaN =', Np-Npp
    #    print ''.join([trans.Vp, trans.Vpp, trans.Qp, trans.Qpp])

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
    s_omegap = qn_to_frac(trans.statep, 'Omega', '   ')
    s_omegapp = qn_to_frac(trans.statepp, 'Omega', '   ')

    Vp = '       %s%s  %s' % (ElecStateLabelp, s_omegap, s_vp)
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
    #Npp = trans.statepp_get('N')
    #if Npp is not None:
    #    Np = trans.statep_get('N')
    #    if Np is not None:
    #        brN = branch.get(Np - Npp)

    #reg = 1    # regular spin-orbit splitting
    #if trans.molec_id == 13:    # OH
    #    reg = -1    # inverted spin-orbit splitting
    # regular spin-orbit splitting:
    # Omega = 0.5 => J = N + 1/2, Omega = 1.5 => J = N - 1/2
    # NB this is wrong for NO in the HITRAN 2004 paper (p.175)
    # (opposite way round for inverted spin-orbit splitting)
    #Omegapp = trans.statepp.get('Omega')
    #if Omegapp < 1.:
    #    Npp = int(Jpp - reg * 0.5)
        # NB for J = 1/2, Omega = 1/2, N must be 1
    #    if Npp == 0:
    #        Npp = 1
    #else:
    #    Npp = int(Jpp + reg * 0.5)
    #Omegap = trans.statep.get('Omega')
    #if Omegap < 1.:
    #    Np = int(Jp - reg * 0.5)
        # NB for J = 1/2, Omega = 1/2, N must be 1
    #    if Np == 0:
    #        Np = 1
    #else:
    #    Np = int(Jp + reg * 0.5)
    #if Npp is not None and Np is not None:
    #    brN = branch.get(Np - Npp, ' ')

    kronig_paritypp = qn_to_str(trans.statepp, 'kronigParity', '%s', ' ')

    s_multipole = ' '
    if trans.multipole == 'M1':
        s_multipole = 'm'    # magnetic dipole
    if trans.molec_id == 13:    # OH
        kronig_parityp = qn_to_str(trans.statep, 'kronigParity', '%s', ' ')
        if trans.iso_id < 3:
            # (16O)H and (18O)H coupling with H gives integer F (I=0.5)
            s_Fp = qn_to_str(trans.statep, 'F', '%5d', ' '*5)
            s_Fpp = qn_to_str(trans.statepp, 'F', '%5d', ' '*5)
        else:
            # (16O)D coupling with D gives half-integer F (I=1)
            s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5)
            s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)
            
        Qpp = ' %s%s%s%s%s%s' % (brN, brJ, s_Jpp, kronig_parityp,
                                    kronig_paritypp, s_Fpp)
        Qp = '          %s' % s_Fp
    else:
        if trans.molec_id == 8: # NO
            # hyperfine coupling only resolved for (14N): I=1, so F is 
            # half-integer
            s_Fp = qn_to_str(trans.statep, 'F', '%5.1f', ' '*5)
            s_Fpp = qn_to_str(trans.statepp, 'F', '%5.1f', ' '*5)
        else: # the only molecule left is trans.molec_id == 18:  # ClO
            # I=1.5 for (35Cl) and (37Cl) so F is integer
            s_Fp = qn_to_str(trans.statep, 'F', '%5d', ' '*5)
            s_Fpp = qn_to_str(trans.statepp, 'F', '%5d', ' '*5)
        Qp = '%s         %s' % (s_multipole, s_Fp)
        Qpp = '  %s%s%s%s%s' % (brN, brJ, s_Jpp, kronig_paritypp, s_Fpp)
    
    return Vp, Vpp, Qp, Qpp
