# -*- coding: utf-8 -*-
# correct_par.py

# Christian Hill, 24/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A method to correct the occasional malformed .par line that crops up in
# the HITRAN database, for the purposes of checking my pyHAWKS output.

def correct_par(trans):
    par_line = trans.par_line
    if trans.molec_id == 6:
        # some of the lines for CH4 have the rovibrational symmetry label
        # formatted to the right instead of the left
        if par_line[80:82] == ' E':
            par_line = par_line[:80] + 'E ' + par_line[82:]
        if par_line[95:97] == ' E':
            par_line = par_line[:95] + 'E ' + par_line[97:]
        # one(?) line has a badly formatted alpha quantum number
        if par_line[119:122] == ' 1 ':
            par_line = par_line[:119] + '  1' + par_line[122:]
        # three more malformed lines
        if par_line[115:122] == '3A2   1':
            par_line = par_line[:115] + ' 3A2  1' + par_line[122:]
        if par_line[115:122] == '3F2   1':
            par_line = par_line[:115] + ' 3F2  1' + par_line[122:]
        if par_line[115:122] == '3F1   1':
            par_line = par_line[:115] + ' 3F1  1' + par_line[122:]

    if trans.molec_id == 10:
        # some negative lower state energies for NO2
        if par_line[48:56] == '-0.00490':
            par_line = par_line[:48] + '-1.00000' + par_line[56:]

    if trans.molec_id == 11:
        # the infamous asSym problem for NH3 - the a/s label is
        # duplicated in the Q and V fields, but for 900 or so lines
        # which are 's' in their lower state, the Q field has 'a'
        if par_line[96] == 's' and par_line[122] == 'a':
            par_line = par_line[:122] + 's' + par_line[123:]
        if trans.local_iso_id == 2:
            # (15N)H3 uses +/- for some lines
            if par_line[122] == '+':
                par_line = par_line[:122] + 's' + par_line[123:]
            if par_line[122] == '-':
                par_line = par_line[:122] + 'a' + par_line[123:]
           
            if par_line[96] == ' ' and par_line[122] in ('a', 's'):
                par_line = par_line[:96] + par_line[122] + par_line[97:]
            if par_line[107] == ' ' and par_line[81] in ('a', 's'):
                par_line = par_line[:107] + par_line[81] + par_line[108:]
            if par_line[122] == ' ' and par_line[96] in ('a', 's'):
                par_line = par_line[:122] + par_line[96] + par_line[123:]

    if trans.molec_id == 13:
        # remove the N-branch designation for OH
        par_line = par_line[:113] + ' ' + par_line[114:]
    if trans.molec_id == 8:
        # remove the N-branch designation for NO and ClO
        par_line = par_line[:114] + ' ' + par_line[115:]

    if trans.molec_id == 8: # NO
        # ' .5' -> '0.5'
        if par_line[124:127] == ' .5':
            par_line = par_line[:124] + '0.5' + par_line[127:]
        if par_line[109:112] == ' .5':
            par_line = par_line[:109] + '0.5' + par_line[112:]

    if trans.molec_id in (24, 27, 28):  # CH3Cl, C2H6, PH3
        # replace default K=-1 designation with whitespace
        if par_line[100:103] == ' -1':
            par_line = par_line[:100] + '   ' + par_line[103:]

    if trans.molec_id in (16,17):
        # some HBr and HI lines have gamma_self formatted as .ddd0 instead
        # of 0.ddd
        if par_line[40] == '.':
            gamma_self = float(par_line[40:45])
            s_gamma_self = '%5.3f' % gamma_self
            par_line = par_line[:40] + s_gamma_self + par_line[45:]

    return par_line
