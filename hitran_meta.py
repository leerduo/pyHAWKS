# -*- coding: utf-8 -*-
# hitran_meta.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# Some useful methods and attributes relating to metadata to the
# HITRAN database.

from hitran_cases import *

def get_case_module(molec_id, iso_id):
    """
    Return the appropriate case_module for describing states of the
    isotopologue identified by HITRAN IDs molec_id and iso_id.

    """

    if molec_id in (5, 14, 15, 16, 17, 22, 36, 46):
        return hcase_dcs
    if molec_id in (1, 3, 9, 21, 31, 37):
        return hcase_nltcs
    print 'Failed to resolve isotopologue to an hcase case_module'
    return None
