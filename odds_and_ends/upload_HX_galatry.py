# -*- coding: utf-8 -*-
# upload_HX_galatry.py

import os
import sys

HOME = os.getenv('HOME')
HITRAN_PATH = '/Users/christian/research/HITRAN/HITRAN2008/updates'
SETTINGS_PATH = '/Users/christian/research/VAMDC/HITRAN/django/HITRAN'
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.db import connection
from hitranmeta.models import Iso
from hitranlbl.models import Trans

cursor = connection.cursor()

try:
    HX = sys.argv[1]
except IndexError:
    print 'usage is:\n%s <HX>\n where <HX> is a molecule name' % sys.argv[0]
    sys.exit(1)
if HX == 'HF':
    iso_ids = (51,110)
    date = '2012-10-31'
    G_filename = os.path.join(HITRAN_PATH,
                              'Hydrogen_Halides/14_hit12_Galatry.txt')
elif HX == 'HCl':
    iso_ids = (52,53,107,108)
    date = '2012-12-04'
    G_filename = os.path.join(HITRAN_PATH,
                              'Hydrogen_Halides/15_hit12_Galatry.txt')
else:
    print 'unknown hydrogen halide:', HX
    sys.exit(1)

isos = Iso.objects.filter(pk__in=iso_ids)
trans = Trans.objects.filter(iso__in=isos).filter(valid_from=date)\
                    .order_by('nu')
print trans.count(),'transitions found'

with open(G_filename, 'r') as fi:
    fi.readline()   # throw away header    
    for t in trans:
        key = '%2d%1d%30s' % (t.iso.molecule_id, int(t.par_line[2]),\
                          t.par_line[67:127])
        line = fi.readline().strip()
        if line[:63] != key:
            print 'keys do not match (db first):\n%s\n%s' % (line[:63], key)
            sys.exit(1)
        fields = line[63:].split()
        gammaG_air = float(fields[0])
        try:
            zG_air = float(fields[1])
        except IndexError:
            zG_air = None
        command = 'INSERT INTO prm_gammaG_air (trans_id, val) VALUES (%d, %f)'\
                        % (t.id, gammaG_air)
        cursor.execute(command)
        if zG_air is not None:
            command = 'INSERT INTO prm_zG_air (trans_id, val) VALUES (%d, %f)'\
                            % (t.id, zG_air)
            cursor.execute(command)
connection.commit()
