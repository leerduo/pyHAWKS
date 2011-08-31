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

    return par_line
