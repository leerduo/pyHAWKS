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

# NB this program expects a configuration file, pyHAWKS_config.py
# containing DATA_DIR and SETTINGS_PATH, the location of the directory
# to create the .states and .trans files in and the location of the Django
# settings.py file respectively.

import os
import sys

from pyHAWKS_config import SETTINGS_PATH
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection, transaction

import time
import datetime
import argparse
from hitran_transition import HITRANTransition
import hitran_meta
from hitran_param import HITRANParam
from fmt_xn import *
import xn_utils
vprint = xn_utils.vprint
from hitranmeta.models import Molecule, Iso, RefsMap, Case
from hitranlbl.models import State, Trans, Qns, Prm
from par2norm import parse_par
from stage_upload import stage_upload
from upload_data import upload_data

from cmdline import parser, process_args

dbname = 'hitran2'
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
