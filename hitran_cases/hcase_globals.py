# -*- coding: utf-8 -*-
# hcase_globals.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_globals module, with general methods to help with the writing
# and parsing the quantum numbers of states in the HITRAN database.

import xn_utils

# a dictionary of branch designations, to and from the corresponding DeltaJ:
# e.g. Jp = Jpp + branch['R'] means Jp = Jpp + 1 and branch[-1] = 'P'
branch = {	'M': -4, 'O': -2, 'P': -1, 'Q': 0, 'R': 1, 'S': 2, 'U': 4,
		-4: 'M', -2: 'O', -1: 'P', 0: 'Q', 1: 'R', 2: 'S', 4: 'U'}

def save_qn(qns, qn_name, qn_str):
    """
    Store the value of qn_str to the dictionary qns under the key qn_name.
    If qn_str can be evaluated as an integer, do that; if not, try float,
    and if that fails, don't store anything. Return whatever was stored if
    the conversion was successful and None otherwise.

    """
 
    qn = xn_utils.str_to_num(qn_str)
    if qn is not None:
        qns[qn_name] = qn
        return qn
    return None

def qn_to_str(qns, qn_name, fmt, s_default):
    """
    Return the string version of quantum number qn_name from the qns
    dictionary (or State instance, which has a get() method) formatted as
    fmt. Return s_default if no quantum number is resolved.

    """

    if qns is None:
        return s_default
    qn_val = qns.get(qn_name)
    if qn_val is None:
        return s_default
    return fmt % qn_val

