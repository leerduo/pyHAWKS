# -*- coding: utf-8 -*-
# hitran_meta.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# Some useful methods and attributes relating to metadata to the
# HITRAN database.

from hitran_cases import *

def get_states(trans):
    """
    Given trans, and instance of HITRANTransition, parse its quantum
    numbers with the appropriate case_module, and return a tuple of:
    case_module: the case module (e.g. hcase_dcs) that understands
                 the HITRAN .par file's format of the quantum numbers
    statep: an instance of the appropriate derived class of State for the
            upper state (e.g. HLtcs -> Ltcs -> State)
    statepp: an instance of the appropriate derived class of State for the
             lower state
    multipole: a string identifying the multipole of this transition,
               e.g. 'E1' for electric dipole, as returned by the case_module's
               method, parse_qns
    """

    case_module = CaseClass = None

    if trans.molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        case_module, CaseClass = hcase_dcs, hdcs.HDcs
    elif trans.molec_id in (1, 3, 9, 21, 31, 37):
        case_module, CaseClass = hcase_nltcs, hnltcs.HNltcs
    elif trans.molec_id in (2, 4, 19, 23):
        case_module, CaseClass = hcase_ltcs, hltcs.HLtcs
    elif trans.molec_id == 6:
        if trans.local_iso_id in (1,2):
            case_module, CaseClass = hcase_sphcs, hsphcs.HSphcs
        elif trans.local_iso_id in (3,4):
            case_module, CaseClass = hcase_stcs, hstcs.HStcs
    elif trans.molec_id == 42:
            case_module, CaseClass = hcase_sphcs, hsphcs.HSphcs
    elif trans.molec_id == 7:
        case_module, CaseClass = hcase_hundb, hhundb.HHundB
    elif trans.molec_id in (11, 28):
        case_module, CaseClass = hcase_pyrtet, hstcs.HStcs
    elif trans.molec_id in (24, 27, 39, 40, 41):
        case_module, CaseClass = hcase_stcs, hstcs.HStcs
    elif trans.molec_id in (12, 20, 25, 29, 32, 38):
        case_module, CaseClass = hcase_asymcs, hasymcs.HAsymcs
    elif trans.molec_id in (10, 33):
        case_module, CaseClass = hcase_nltos, hnltos.HNltos
    elif trans.molec_id in (8, 18):
        case_module, CaseClass = hcase_hunda, hhunda.HHundA
    elif trans.molec_id in (26,44):
        case_module, CaseClass = hcase_lpcs, hlpcs.HLpcs
    elif trans.molec_id == 13:
        # OH
        if trans.nu.val > 25000.:
            # A(2Sigma+)-X(2Pi) transitions in the UV
            # deal with this as a special case, because the upper and lower
            # states belong to different cases (Hund's case (b) and (a)).
            case_module = hcase_OHAX
            qnsp, qnspp, multipole = case_module.parse_qns(trans)
            statep = hhundb.HHundB(trans.molec_id, trans.local_iso_id,
                           trans.global_iso_id, trans.Eupper, None,
                           trans.gp, qnsp)
            statepp = hhunda.HHundA(trans.molec_id, trans.local_iso_id,
                            trans.global_iso_id, trans.Elower, None,
                            trans.gpp, qnspp)
            return case_module, statep, statepp, multipole
        else:
            # X(2Pi)-X(2Pi) transitions
            case_module, CaseClass = hcase_hunda, hhunda.HHundA
        

    if case_module and CaseClass:
        qnsp, qnspp, multipole = case_module.parse_qns(trans)
        statep = CaseClass(trans.molec_id, trans.local_iso_id,
                           trans.global_iso_id, trans.Eupper, None,
                           trans.gp, qnsp)
        statepp = CaseClass(trans.molec_id, trans.local_iso_id,
                            trans.global_iso_id, trans.Elower, None,
                            trans.gpp, qnspp)
        return case_module, statep, statepp, multipole

    print 'Unrecognised molec_id, local_iso_id =', trans.molec_id,\
                                                   trans.local_iso_id
    return None, None, None, None

def get_case_module(molec_id, local_iso_id):
    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hcase_dcs
    elif molec_id in (1, 3, 9, 21, 31, 37):
        return hcase_nltcs
    elif molec_id in (2, 4, 19, 23):
        return hcase_ltcs
    elif molec_id == 6:
        if local_iso_id in (1, 2):
            return hcase_sphcs
        elif local_iso_id in (3, 4):
            return hcase_stcs
    elif molec_id == 42:
            return hcase_sphcs
    elif molec_id == 7:
        return hcase_hundb
    elif molec_id in (11, 28):
        return hcase_pyrtet
    elif molec_id in (24, 27, 39, 40, 41):
        return hcase_stcs
    elif molec_id in (12, 20, 25, 29, 32, 38):
        return hcase_asymcs
    elif molec_id in (10, 33):
        return hcase_nltos
    elif molec_id in (8, 13, 18):
        return hcase_hunda
    elif molec_id in (26, 44):
        return hcase_lpcs

    print 'Unrecognised molec_id, local_iso_id =', molec_id, local_iso_id
    return None

def get_case_class(molec_id, local_iso_id, ElecStateLabel='X'):
    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hdcs.HDcs
    elif molec_id in (1, 3, 9, 21, 31, 37):
        return hnltcs.HNltcs
    elif molec_id in (2, 4, 19, 23):
        return hltcs.HLtcs
    elif molec_id == 6:
        if local_iso_id in (1, 2):
            return hsphcs.HSphcs
        elif local_iso_id in (3, 4):
            return hstcs.HStcs
    elif molec_id == 42:
            return hsphcs.HSphcs
    elif molec_id == 7:
        return hhundb.HHundB
    elif molec_id in (11, 24, 27, 28, 39, 40, 41):
        return hstcs.HStcs
    elif molec_id in (12, 20, 25, 29, 32, 38):
        return hasymcs.HAsymcs
    elif molec_id in (10, 33):
        return hnltos.HNltos
    elif molec_id in (8, 18):
        return hhunda.HHundA
    elif molec_id in (26, 44):
        return hlpcs.HLpcs
    elif molec_id == 13:
        if ElecStateLabel == 'A':
            # OH A(2Sigma+) is Hund's case (b)
            return hhundb.HHundB
        # OH X(2Pi) is Hund's case (a)
        return hhunda.HHundA

    print 'Unrecognised molec_id, local_iso_id =', molec_id, local_iso_id
    return None

