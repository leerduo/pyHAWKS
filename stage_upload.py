# -*- coding: utf-8 -*-
# stage_upload.py

# v0.2
# Christian Hill, 5/8/12
#
# Stage the transitions file for upload to the database by identifying
# transitions that are already in the database, and transitions that
# need to be expired.

import os
import sys
import re
import time
import datetime
from fmt_xn import trans_fields
import xn_utils
vprint = xn_utils.vprint

from pyHAWKS_config import SETTINGS_PATH
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranlbl.models import Trans

def write_db_trans(args, molecule, isos):
    """
    Write the current valid transitions to a file called db_trans_file,
    which will be compared to the file of transitions to be uploaded to
    decide which are still valid (haven't changed) which to expire.

    """

    vprint('Retrieving existing transitions from database...')

    today = datetime.date.today()
    fo = open(args.db_trans_file, 'w')
    fo_id = open(args.db_trans_file_id, 'w')
    db_transitions = Trans.objects.filter(iso__in=isos)\
                         .filter(valid_to__gt=today).order_by('nu')
    n_db_trans = db_transitions.count()
    vprint('%d currently valid transitions found.' % n_db_trans)
    
    vprint('Writing currently valid transitions to %s ...'% args.db_trans_file)
    perc = 0; perc_thresh = 0
    for i, trans in enumerate(db_transitions):

        perc = float(i)/n_db_trans * 100
        if perc > perc_thresh:
            vprint('%d %%' % perc_thresh, 1)
            perc_thresh += 1

        trans.stateIDp = trans.statep.id
        trans.stateIDpp = trans.statepp.id
        trans.molec_id = molecule.id
        trans.local_iso_id = trans.iso.isoID
        try:
            trans.flag = trans.par_line[145]
        except IndexError:
            trans.flag = ' '

        for prm in trans.prm_set.all():
            exec('trans.%s = prm' % prm.name)

        s_vals = []
        for trans_field in trans_fields:
            # translate <prm>.ref to <prm>.source.id
            if trans_field.name.endswith('.ref'):
                trans_field.name = '%s.source.id' % transfield[:-4]
            try:
                val = eval('trans.%s' % trans_field.name)
            except AttributeError:
                val = None
            if val is None:
                s_vals.append(trans_field.default)
            else:
                s_vals.append(trans_field.fmt % val)
                
        print >>fo, ','.join(s_vals)
        print >>fo_id, trans.id
    fo.close()
    fo_id.close()

def stage_upload(args, molecule, isos):
    """
    Stage the transtions file for upload to the database by identifying
    transitions that are already in the database, and transitions that
    need to be expired.

    """

    write_db_trans(args, molecule, isos)

    # find out where the old and new transitions differ
    vprint('calculating the diff ...')
    os.system('diff %s %s > %s' % (args.db_trans_file, args.trans_file,
                                   args.diff_file))
    vprint('done.')

    db_trans_ids = []
    vprint('Writing expire-ids file and upload transitions file...')
    fi_id = open(args.db_trans_file_id, 'r')
    for line in fi_id:
        db_trans_ids.append(int(line))

    patt = '^(\d+),?(\d+)?[c|d]'
    fo_upload = open(args.trans_file_upload, 'w')
    fo_expire_id = open(args.db_expire_id, 'w')
    for line in open(args.diff_file, 'r'):
        if line[0] == '>':
            line = line.rstrip()    # strip the EOL
            print >>fo_upload, line[2:] # remove '> '
            continue
        m = re.match(patt, line)
        if m:
            l1 = int(m.group(1))
            l2 = l1
            if m.group(2):
                l2 = int(m.group(2))
            for i in range(l1-1,l2):
                print >>fo_expire_id, db_trans_ids[i]
    fo_expire_id.close()
    fo_upload.close()
        

        
            


