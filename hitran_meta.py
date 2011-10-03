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

    case_module = CaseClass = None

    if trans.molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        case_module, CaseClass = hcase_dcs, hdcs.HDcs
    elif trans.molec_id in (1, 3, 9, 21, 31, 37):
        case_module, CaseClass = hcase_nltcs, hnltcs.HNltcs
    elif trans.molec_id in (2, 4, 19, 23):
        case_module, CaseClass = hcase_ltcs, hltcs.HLtcs
    elif trans.molec_id == 6:
        if trans.iso_id in (1,2):
            case_module, CaseClass = hcase_sphcs, hsphcs.HSphcs
        elif trans.iso_id in (3,4):
            case_module, CaseClass = hcase_stcs, hstcs.HStcs
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
    elif trans.molec_id in (8, 13, 18):
        case_module, CaseClass = hcase_hunda, hhunda.HHundA
    elif trans.molec_id == 26:
        case_module, CaseClass = hcase_lpcs, hlpcs.HLpcs

    if case_module and CaseClass:
        qnsp, qnspp, multipole = case_module.parse_qns(trans)
        statep = CaseClass(trans.molec_id, trans.iso_id, trans.Eupper, None,
                      trans.gp, qnsp)
        statepp = CaseClass(trans.molec_id, trans.iso_id, trans.Elower, None,
                      trans.gpp, qnspp)
        return case_module, statep, statepp, multipole

    print 'Unrecognised molec_id, iso_id =', trans.molec_id, trans.iso_id
    return None, None, None, None

def get_case_module(molec_id, iso_id):
    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hcase_dcs
    elif molec_id in (1, 3, 9, 21, 31, 37):
        return hcase_nltcs
    elif molec_id in (2, 4, 19, 23):
        return hcase_ltcs
    elif molec_id == 6:
        if iso_id in (1, 2):
            return hcase_sphcs
        elif iso_id in (3, 4):
            return hcase_stcs
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
    elif molec_id == 26:
        return hcase_lpcs

    print 'Unrecognised molec_id, iso_id =', molec_id, iso_id
    return None

def get_case_class(molec_id, iso_id):
    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hdcs.HDcs
    elif molec_id in (1, 3, 9, 21, 31, 37):
        return hnltcs.HNltcs
    elif molec_id in (2, 4, 19, 23):
        return hltcs.HLtcs
    elif molec_id == 6:
        if iso_id in (1, 2):
            return hsphcs.HSphcs
        elif iso_id in (3, 4):
            return hstcs.HStcs
    elif molec_id == 7:
        return hhundb.HHundB
    elif molec_id in (11, 24, 27, 28, 39, 40, 41):
        return hstcs.HStcs
    elif molec_id in (12, 20, 25, 29, 32, 38):
        return hasymcs.HAsymcs
    elif molec_id in (10, 33):
        return hnltos.HNltos
    elif molec_id in (8, 13, 18):
        return hhunda.HHundA
    elif molec_id == 26:
        return hlpcs.HLpcs

    print 'Unrecognised molec_id, iso_id =', molec_id, iso_id
    return None

