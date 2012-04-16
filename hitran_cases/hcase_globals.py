# -*- coding: utf-8 -*-
# hcase_globals.py

# Christian Hill, 19/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# The hcase_globals module, with general methods to help with the writing
# and parsing the quantum numbers of states in the HITRAN database.

import re
import xn_utils

# a dictionary of branch designations, to and from the corresponding DeltaJ:
# e.g. Jp = Jpp + branch['R'] means Jp = Jpp + 1 and branch[-1] = 'P'
# also used for DeltaN, hence the large possible branch deltas
branch = { 'K': -6, 'L': -5, 'M': -4, 'N': -3, 'O': -2, 'P': -1, 'Q': 0,
           'R': 1, 'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6,
		   -6: 'K', -5: 'L', -4: 'M', -3: 'N', -2: 'O', -1: 'P', 0: 'Q',
            1: 'R', 2: 'S', 3: 'T', 4: 'U', 5: 'V', 6: 'W'}

vib_qn_patt = '^v(\d+)$'    # regexp matching vibrational quantum number name

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

def save_qn_str(qns, qn_name, qn_str):
    """
    Store qn_str, stripped of whitespace, to the dictionary qns under the
    key qn_name. If qn_str is empty or just whitespace, don't store anything
    and return None; otherwise return whatever was stored.

    """
    if qn_str is None:
        return None
    qn = qn_str.strip()
    if qn:
        qns[qn_name] = qn
        return qn
    return None

def qn_to_frac(qns, qn_name, s_default):
    """
    Return the value of qns, formatted as a fraction, or s_default if this
    isn't possible. NB we only deal with half-integral numbers and there
    is no control over the size of the string returned.

    """

    if qns is None:
        return s_default
    qn_val = qns.get(qn_name)
    if qn_val is None:
        return s_default
    num = 2 * qn_val
    if qn_val % 2:
        # half odd-integer
        return '%d/2' % num
    # integer
    return str(num)

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

def qn_to_str_ljust(qns, qn_name, field_size, s_default):
    """
    As for qn_to_str, but ensure that the string returned has the quantum
    number or symmetry qn_name justified in a string of length field_size.

    """

    if qns is None:
        return s_default
    qn_val = qns.get(qn_name)
    if qn_val is None:
        return s_default
    return qn_val.ljust(field_size)

def set_normal_modes_V(state):
    s_v = {}
    total_vib_quanta = 0
    nv = 0
    for qn_name in state.keys():
        m = re.match(vib_qn_patt, qn_name)
        if not m:
            continue
        s_mode = m.group(1)
        nv += 1
        mode = int(s_mode)
        val = state[qn_name]
        total_vib_quanta += val
        if val > 1:
            s_v[mode] = '%dV%d' % (val, mode)
        else:
            s_v[mode] = 'V%d' % mode
    if nv == 0:
        return ' '*15
    if total_vib_quanta == 0:
        return '         GROUND'
    modes = s_v.keys()
    modes.sort()
    V = '+'.join(['%s' % s_v[mode] for mode in modes])
    return '%15s' % V 

def get_normal_modes_V(V):
    s_V = V.strip()
    if not s_V:
        # unassigned vibrational state
        return []
    if s_V == 'GROUND':
        # ground vibrational state - indicate this with vi=0 for i=1,2,3,4:
        return [('v1', 0), ('v2', 0), ('v3', 0), ('v4', 0)]
    s_vibs = s_V.split('+')
    vqns = []
    for i, s_vib in enumerate(s_vibs):
        if s_vib[0] == 'V':
            n=1     # states with 1 quantum of vi are given as Vi, not 1Vi
            mode  = 'v%s' % s_vib[1:]
        else:
            n=int(s_vib[0])
            mode  = 'v%s' % s_vib[2:]
        vqns.append((mode, n))
    return vqns
