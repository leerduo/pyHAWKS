#!/usr/bin/env python
# -*- coding: utf-8 -*-
# update_db.py

# Christian Hill, 12/4/12
# Department of Physics and Astronomy, University College London
# christian.hill@ucl.ac.uk
#
# A script to parse a given .par file in the native HITRAN2004+ format
# and extract the relevant data for update to the relational database.
# Only states and transitions that have changed from those already in the
# database are saved in .states and .trans files - ie this creates a patch.

# NB this program expects to find a directory
# $DATA_DIR = $HOME/research/HITRAN/data/hitran
# into which it puts the .states and .trans files.
# One must also specify the location of the Django HITRAN project's
# settings file - see below: $HOME/research/VAMDC/HITRAN/django/HITRAN

import os
import sys

HOME = os.getenv('HOME')
DATA_DIR = os.path.join(HOME, 'research/HITRAN/data/hitran')
SETTINGS_PATH = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import time
import datetime
import argparse
from hitran_transition import HITRANTransition
from fmt_xn import *
from hitranmeta.models import Iso

dbname = 'hitran'

# command line arguments:
parser = argparse.ArgumentParser(description='Update the HITRAN MySQL'
            ' database with a patch from the provided .par file in'
            ' native HITRAN2004+ format')
parser.add_argument('par_file', metavar='<par_file>',
        help='the .par file, and root of the filenames <filestem>.states'
             ' and <filestem>.trans')
parser.add_argument('-O', '--overwrite', dest='overwrite',
        action='store_const', const=True, default=False,
        help='overwrite .states and .trans files, if present')
args = parser.parse_args()
overwrite = args.overwrite
filestem, ext = os.path.splitext(args.par_file)
if ext not in ('', '.par'):
    print 'par_file must end in .par or be given without extension; I got'
    print args.par_file
    sys.exit(1)
par_file = '%s.par' % filestem
filestem = os.path.basename(filestem)

# get the Iso objects from the molecID, taken from the par_file filename
try:
    molecID = int(filestem.split('_')[0])
except:
    print 'couldn\'t parse molecID from filestem %s' % filestem
    print 'the filename should start with "<molecID>_"'
    sys.exit(1)
isos = Iso.objects.filter(molecule__molecID=molecID).order_by('isoID')

from hitranmeta.models import *
from hitranlbl.models import *

if not os.path.exists(par_file):
    print 'No such file: %s' % par_file
    sys.exit(1)

if not os.path.exists(DATA_DIR):
    print 'Oops. I want to put my .states and .trans files in directory:'
    print DATA_DIR
    print 'but it doesn\'t exist.'
    sys.exit(1)

mod_date = datetime.date.fromtimestamp(os.path.getmtime(par_file)).isoformat()
print 'From file modification date, taking the from-date to be', mod_date

# the output files will be:
# $DATA_DIR/<filestem>-YYYY-MM-DD.states and .trans
# where <filestem> is typically <molec_ID>_hit<yr> with <yr> the 2-digit
# year of the update, and YYYY-MM-DD is the modification date of the
# .par file
trans_file = os.path.join(DATA_DIR, '%s.%s.trans' % (filestem, mod_date))
states_file = os.path.join(DATA_DIR, '%s.%s.states' % (filestem, mod_date))
print '%s\n-> %s\n   %s' % (par_file, trans_file, states_file)

if not overwrite:
    # the .trans and .states files should not already exist
    for filename in (trans_file,states_file):
        if os.path.exists(filename):
            print 'File exists:\n%s\nAborting.' % filename
            sys.exit(1)

# read the lines and rstrip them of the EOL characters. We don't lstrip
# because we keep the space in front of molecIDs 1-9
lines = [x.rstrip() for x in open(par_file, 'r').readlines()]
states = {}
fo_s = open(states_file, 'w')
fo_t = open(trans_file, 'w')
start_time = time.time()
# find out the ID at which we can start adding states
first_stateID = State.objects.all().order_by('-id')[0].id + 1
stateID = first_stateID

def locate_state_in_db(state):
    """
    Try to find state in the database table modelled by the State class;
    returns None if the state isn't found, or the state's primary key id
    if it is.

    """
     
    # find all the states in the database with the same quantum numbers as
    # the state we're seeking:
    dbstates = State.objects.filter(iso=isos[state.iso_id-1])\
                        .filter(s_qns=state.serialize_qns())
    if not dbstates:
        return None
    for dbstate in dbstates:
        # look through the states to see if everything else matches:
        if dbstate.str_rep() == state.str_rep():
            return dbstate.id
    # nothing matched; return None
    #print dbstate.str_rep(), state.str_rep()
    return None

def locate_trans_in_db(trans):
    """
    Try to find trans in the database table modelled by the Trans class;
    returns None if the transition isn't found, or the transition's primary
    key id if it is.

    """

    # find all the transitions in the database with the same wavenumber as
    # the transition we're seeking:
    dbtranss = Trans.objects.filter(iso=isos[trans.statepp.iso_id-1])\
                        .filter(nu=trans.nu.val).filter(Sw=trans.Sw.val)
    if not dbtranss:
        return None
    for dbtrans in dbtranss:
        #if dbtrans.str_rep() == dbtrans.str_rep():
        # XXX for now just compare par_line, which is quicker and sufficient
        # if there are no parameters beyond gamma_air, gamma_self, n_air, d_air
        if dbtrans.par_line == dbtrans.par_line:
            return dbtrans.id
    return None

found_states = 0
found_trans = 0
for i,line in enumerate(lines[:100]):       # XXX
    trans = HITRANTransition.parse_par_line(line)
    if trans is None:
        # blank or comment line
        continue

    new_trans = False
    # upper state
    this_stateID = locate_state_in_db(trans.statep)
    if this_stateID:
        # this state is already in the database; set trans.stateIDp
        trans.stateIDp = this_stateID
        found_states += 1
    else:
        # this state isn't in the database: keep track of it in states[]
        statep_str_rep = trans.statep.str_rep()
        if statep_str_rep not in states:
            # we've not seen this upper state before: save it and write it
            # to fo_s
            trans.stateIDp = stateID
            states[statep_str_rep] = stateID
            stateID += 1
            print >>fo_s, trans.statep.to_str(state_fields, ',')
        else:
            trans.stateIDp = states[statep_str_rep]
        # if a transition references a new state, it's a new transition
        new_trans = True
    # lower state
    this_stateID = locate_state_in_db(trans.statepp)
    if this_stateID:
        # this state is already in the database; set trans.stateIDpp
        trans.stateIDpp = this_stateID
        found_states += 1
    else:
        # this state isn't in the database: keep track of it in states[]
        statepp_str_rep = trans.statepp.str_rep()
        if statepp_str_rep not in states:
            # we've not seen this lower state before: save it and write it
            # to fo_s
            trans.stateIDpp = stateID
            states[statepp_str_rep] = stateID
            stateID += 1
            print >>fo_s, trans.statepp.to_str(state_fields, ',')
        else:
            trans.stateIDpp = states[statepp_str_rep]
        # if a transition references a new state, it's a new transition
        new_trans = True

    # now look at the transition
    if new_trans:
        # its got at least one new state, so it's a new transition
        print >>fo_t, trans.to_str(trans_fields, ',')
        continue
    this_transID = locate_trans_in_db(trans)
    if not this_transID:
        # this is a new transition: store it and move on
        print >>fo_t, trans.to_str(trans_fields, ',')
        continue

    # if we're here, it's because the transition is already in the database
    found_trans += 1
    continue

fo_t.close()
fo_s.close()
print '%d states were already in the database' % found_states
print '%d new or updated states were identified' % (stateID-first_stateID)
print '%d transitions were already in the database' % found_trans

end_time = time.time()
print '%d transitions and %d states in %.1f secs' % (len(lines), len(states),
            end_time - start_time)
