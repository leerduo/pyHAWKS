# -*- coding: utf-8 -*-
# stage_upload.py

# v0.2
# Christian Hill, 5/8/12
#
# Stage the transitions file for upload to the database by identifying
# transitions that are already in the database, and transitions that
# need to be expired.
# NB updates to the database must be applied in chronological order, or
# this routine will get very confused and mess up the database for the
# molecule it's supposed to be updating.
# NB stage_upload calls the system routine diff. So it might not work
# on Windows...

import os
import sys
import re
import time
import datetime
from fmt_xn import trans_prms, trans_fields
from xn_utils import vprint

from pyHAWKS_config import SETTINGS_PATH
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import connection
from hitranlbl.models import Trans, Prm

def write_db_trans(args, molecule, isos):
    """
    Write the transitions currently in the database and currently valid to a
    file called db_trans_file, which will be compared to the file of
    transitions to be uploaded to decide which are still valid (haven't
    changed) which to expire.

    """

    cursor = connection.cursor()
    vprint('Retrieving existing transitions from database...')

    today = datetime.date.today()
    # db_trans_file will hold a list of the currently valid transitions for
    # the molecule of interest
    fo = open(args.db_trans_file, 'w')
    # db_trans_file_id will hold a list of the transition IDs corresponding
    # to each line of db_trans_file
    fo_id = open(args.db_trans_file_id, 'w')
    # fetch the currently valid transitions for all the isotopologues of our
    # molecule
    db_transitions = Trans.objects.filter(iso__in=isos)\
                         .filter(valid_to__gt=today).order_by('nu')
    n_db_trans = db_transitions.count()
    vprint('%d currently valid transitions found.' % n_db_trans)
    
    vprint('Writing currently valid transitions to %s ...'% args.db_trans_file)
    percent = 0; percent_thresh = 0 # for the progress indicator
    for i, trans in enumerate(db_transitions):

        # a progress indicator of percent completion
        percent = float(i)/n_db_trans * 100
        if percent > percent_thresh:
            vprint('%d %%' % percent_thresh, 1)
            percent_thresh += 1

        # a bit of translation so that everything we need for the string
        # representation of the transition is an immediate attribute of trans
        trans.stateIDp = trans.statep.id
        trans.stateIDpp = trans.statepp.id
        trans.molec_id = molecule.id
        trans.local_iso_id = trans.iso.isoID
        try:
            trans.flag = trans.par_line[145]
        except IndexError:
            trans.flag = ' '

        # get the parameters for this transition
        for prm in trans_prms:
            command = 'SELECT * FROM prm_%s WHERE trans_id=%d'\
                         % (prm.lower(), trans.id)
            cursor.execute(command)
            rows = cursor.fetchall()
            if not rows:
                # this parameter apparently doesn't exist for this transition
                continue
            # make a generic Prm object named for the parameter, and with
            # the attributes val, err, ierr and source_id in that order:
            #globals()[prm] = Prm(*rows[0][1:])
            setattr(trans, prm, Prm(*rows[0][1:]))
            
        # build a list of strings, each of which is a field in the
        # db_trans_file output
        s_vals = []
        for trans_field in trans_fields:
            try:
                val = eval('trans.%s' % trans_field.name)
                if val is None:
                    s_vals.append(trans_field.default)
                else:
                    s_vals.append(trans_field.fmt % val)
            except AttributeError:
                # no value for this field - use the default
                s_vals.append(trans_field.default)
            #except TypeError:
            #    vprint('None value for trans_field %s' % trans_field.name)

        # write the fields, separated by commas in case someone is
        # foolish enough to think it a good idea to read the file in Excel
        print >>fo, ','.join(s_vals)
        # and write the transition ID in the parallel db_trans_file_id file
        print >>fo_id, trans.id
    fo.close()
    fo_id.close()

def stage_upload(args, molecule, isos):
    """
    Stage the transtions file for upload to the database by identifying
    transitions that are already in the database, and transitions that
    need to be expired.

    """

    # first write the currently valid transitions to db_trans_file and
    # their IDs to db_trans_file_id
    write_db_trans(args, molecule, isos)

    # find out where the old and new transitions differ
    # I'm not clever enough to do this fast in Python (the files involved
    # can be much larger than the available memory), so farm it out to the
    # Unix tool diff, which produces the diff_file 
    vprint('calculating the diff ...')
    os.system('diff %s %s > %s' % (args.db_trans_file, args.trans_file,
                                   args.diff_file))
    vprint('done.')

    vprint('Writing expire-ids file and upload transitions file...')
    # get the list of the currently-valid transitions' IDs from
    # db_trans_file_id
    db_trans_ids = []
    fi_id = open(args.db_trans_file_id, 'r')
    for line in fi_id:
        db_trans_ids.append(int(line))

    # trans_file_upload will hold the string representations of transitions 
    # new or altered transitions to be uploaded to the database
    fo_upload = open(args.trans_file_upload, 'w')

    # db_expire_id will hold the IDs of currently-valid transitions which
    # are to be expired (usually because they're being replaced with better
    # versions from trans_file_upload
    fo_expire_id = open(args.db_expire_id, 'w')

    # regular expression for the marker in the diff_file indicating changed
    # or deleted lines in the db_trans_file - ie transitions to be expired
    patt = '^(\d+),?(\d+)?[c|d]'
    for line in open(args.diff_file, 'r'):
        if line[0] == '>':
            # this line is a transition to be uploaded
            line = line.rstrip()    # strip the EOL
            print >>fo_upload, line[2:] # remove '> '
            continue

        m = re.match(patt, line)
        if m:
            # l1-l2 is the line number range to which this group of
            # changed or deleted lines applies
            l1 = int(m.group(1))
            l2 = l1
            if m.group(2):
                l2 = int(m.group(2))
            # write the expired lines' ids to the db_expire_id file
            for i in range(l1-1,l2):
                print >>fo_expire_id, db_trans_ids[i]

    fo_expire_id.close()
    fo_upload.close()
        

        
            


