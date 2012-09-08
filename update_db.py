#!/usr/bin/env python
# -*- coding: utf-8 -*-
# update_db.py

version = '0.2'
# Christian Hill, 3/8/12
# v0.1
# Christian Hill, 12/4/12
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to parse a given .par file in the native HITRAN2004+ format
# and extract the relevant data for update to the relational database.

import sys

from xn_utils import vprint
from par2norm import parse_par
from stage_upload import stage_upload
from upload_data import upload_data

from cmdline import parser, process_args

args = parser.parse_args()
molecule, isos, d_refs = process_args(args)

vprint('\n\n%s - v%s' % (sys.argv[0], version), 5)
vprint('Christian Hill - christian.hill@ucl.ac.uk', 3)

if args.parse_par:
    parse_par(args, molecule, isos, d_refs)

if args.stage_upload:
    stage_upload(args, molecule, isos)

if args.upload or args.dry_run:
    upload_data(args, molecule, isos, d_refs)
