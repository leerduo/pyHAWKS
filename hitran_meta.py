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
    if trans.molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        case_module, CaseClass = hcase_dcs, hdcs.HDcs
    elif trans.molec_id in (1, 3, 9, 21, 31, 37):
        case_module, CaseClass = hcase_nltcs, hnltcs.HNltcs
    elif trans.molec_id in (2, 4, 19, 23):
        case_module, CaseClass = hcase_ltcs, hltcs.HLtcs
    elif trans.molec_id == 7:
        case_module, CaseClass = hcase_hundb, hhundb.HHundB

    if case_module and CaseClass:
        qnsp, qnspp, multipole = case_module.parse_qns(trans)
        statep = CaseClass(trans.molec_id, trans.iso_id, trans.Eupper, None,
                      trans.gp, qnsp)
        statepp = CaseClass(trans.molec_id, trans.iso_id, trans.Elower, None,
                      trans.gpp, qnspp)
        return case_module, statep, statepp, multipole

    return None, None, None, None

def get_case_module(molec_id, iso_id):
    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hcase_dcs
    elif molec_id in (1, 3, 9, 21, 31, 37):
        return hcase_nltcs
    elif molec_id in (2, 4, 19, 23):
        return hcase_ltcs
    elif molec_id == 7:
        return hcase_hundb

def get_case_class(molec_id, iso_id):
    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hdcs.HDcs
    elif molec_id in (1, 3, 9, 21, 31, 37):
        return hnltcs.HNltcs
    elif molec_id in (2, 4, 19, 23):
        return hltcs.HLtcs
    elif molec_id == 7:
        return hhundb.HHundB

