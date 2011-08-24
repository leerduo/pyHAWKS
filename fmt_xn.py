# -*- coding: utf-8 -*-
# fmt_xn.py

# Christian Hill, 24/8/11
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# Lists of formats for state and transition parameters. Each entry is
# a tuple of the form (<name>, <fmt>, <default>) where <name> is the name
# of the parameter (returning its value under eval within the relevant
# class instance), <fmt> is the formatting string, and <default> is a string
# to be returned if <name> doesn't exist or is None.

state_fields = [('molec_id', '%2d', '  '), ('iso_id', '%1d', ' '),
                ('E', '%10.4f', ' '*10),
                ('g', '%5d', ' '*5), ('serialize_qns()', '%s', '')]

trans_prms = ['nu', 'Sw', 'A', 'gamma_air', 'gamma_self', 'n_air', 'delta_air']
trans_fields = [('molec_id', '%2d', '  '), ('iso_id', '%1d', ' '),
                ('nu.val', '%12.6f', ' '*12), ('nu.err', '%8.1e', ' '*8),
                ('nu.ref', '%3d', '   '),
                ('Sw.val', '%10.3e', ' '*10), ('Sw.err', '%8.1e', ' '),
                ('Sw.ref', '%3d', '   '), ('A.val', '%10.3e', ' '*10),
                ('A.err', '%8.1e', ' '*8), ('A.ref', '%3d', '   '),
                ('Elower', '%10.4f', ' '*10),
                ('gamma_air.val', '%6.4f', ' '*6),
                ('gamma_air.err', '%8.1e', ' '*8),
                ('gamma_air.ref', '%3d', '   '),
                ('gamma_self.val', '%6.4f', ' '*6),
                ('gamma_self.err', '%8.1e', ' '*8),
                ('gamma_self.ref', '%3d', '   '),
                ('n_air.val', '%5.2f', ' '*5),
                ('n_air.err', '%8.1e', ' '*8),
                ('n_air.ref', '%3d', '   '),
                ('delta_air.val', '%9.6f', ' '*9),
                ('delta_air.err', '%8.1e', ' '*8),
                ('delta_air.ref', '%3d', '   '),
                ('stateIDp', '%12d', ' '*12), ('stateIDpp', '%12d', ' '*12),
                ('multipole', '%2s', '  '), ('flag', '%1s', ' '),
                ('gp', '%5d', ' '*5), ('gpp', '%5d', ' '*5),
                ('par_line', '%160s', '*'*160)]

