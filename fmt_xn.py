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

from lbl.output_field import OutputField

state_fields = [OutputField('id', '%12d', 'int'),
                OutputField('global_iso_id', '%4d', int),
                OutputField('E', '%10.4f', float),
                OutputField('g', '%5d', int),
                OutputField('serialize_qns()', '%s', str)]

trans_prms = ['nu', 'Sw', 'A', 'gamma_air', 'gamma_self', 'n_air', 'delta_air']
trans_fields = [
                OutputField('stateIDp', '%12d', int),
                OutputField('stateIDpp', '%12d', int),
                OutputField('molec_id', '%2d', int),
                OutputField('local_iso_id', '%1d', int),
                OutputField('Elower', '%10.4f', float),
                OutputField('gp', '%5d', int),
                OutputField('gpp', '%5d', int),
                OutputField('multipole', '%2s', str),
                OutputField('flag', '%1s', str),

                OutputField('nu.val', '%12.6f', float),
                OutputField('nu.err', '%8.1e', float),
                OutputField('nu.source_id', '%4d', int),
                OutputField('Sw.val', '%10.3e', float),
                OutputField('Sw.err', '%8.1e', float),
                OutputField('Sw.source_id', '%4d', int),
                OutputField('A.val', '%10.3e', float),
                OutputField('A.err', '%8.1e', float),
                OutputField('A.source_id', '%4d', int),
                OutputField('gamma_air.val', '%6.4f', float),
                OutputField('gamma_air.err', '%8.1e', float),
                OutputField('gamma_air.source_id', '%4d', int),
                OutputField('gamma_self.val', '%6.4f', float),
                OutputField('gamma_self.err', '%8.1e', float),
                OutputField('gamma_self.source_id', '%4d', int),
                OutputField('n_air.val', '%5.2f', float),
                OutputField('n_air.err', '%8.1e', float),
                OutputField('n_air.source_id', '%4d', int),
                OutputField('delta_air.val', '%9.6f', float),
                OutputField('delta_air.err', '%8.1e', float),
                OutputField('delta_air.source_id', '%4d', int),

                OutputField('par_line', '%160s', str, '*'*160)
               ]

