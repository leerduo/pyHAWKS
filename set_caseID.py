#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import MySQLdb

# Django needs to know where to find the HITRAN project's settings.py:
HOME = os.getenv('HOME')
hitran_path = os.path.join(HOME,'research/VAMDC/HITRAN/django/HITRAN')
sys.path.append(hitran_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from hitranmeta.models import *
from hitranlbl.models import *
from hitran_meta import *
from HITRAN_configs import *

conn = MySQLdb.connect(host='localhost', user=username, db=dbname,
                       passwd=password)
cursor = conn.cursor()

isos = Iso.objects.all()
for iso in isos:
    molecID = iso.molecule.molecID
    isoID = iso.isoID
    try:
        case_class = get_case_class(molecID, isoID)
        caseID = case_class.caseID
        case_prefix = case_class.case_prefix
    except:
        continue
    #print iso.iso_name, molecID, isoID, case_class.case_prefix
    print iso.id, caseID, case_prefix

    command = 'UPDATE hitranmeta_iso SET case_id=%d WHERE id=%d'\
                % (caseID, iso.id)
    print command
    cursor.execute(command)
conn.commit()
conn.close()
    
    

