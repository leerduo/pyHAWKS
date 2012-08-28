#!/usr/bin/env python
# prm2outputfield.py
import os
import sys
import re
import xn_utils

from pyHAWKS_config import SETTINGS_PATH
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranmeta.models import PrmDesc, OutputField

try:
    prm_name = sys.argv[1]
    cfmt = sys.argv[2]
except IndexError:
    print 'usage is:'
    print '%s <prm_name> <cfmt>' % sys.argv[0]

try:
    prm_desc = PrmDesc.objects.all().filter(name=prm_name).get()
except PrmDesc.DoesNotExist:
    print 'no parameter description found for %s' % prm_desc
    sys.exit(1)

print prm_desc
modifiers = {
    'val': 'the',
    'err': 'absolute error in the',
    'ierr': 'integer error code for the',
    'ref': 'reference ID for the'
}
cfmts = {
    'val': cfmt,
    'err': '%8.6e',
    'ref': '%5d',
    'ierr': '%1d'
}
patt = '%(\d+)'
for suffix, modifier in modifiers.items():
    name = '%s.%s' % (prm_name, suffix)
    name_html = '%s(%s)' % (prm_desc.name_html, suffix)
    cfmt = cfmts[suffix]
    ffmt = xn_utils.cfmt2ffmt(cfmts[suffix])
    desc = '%s %s' % (modifier, prm_desc.description)
    desc_html = '%s %s' % (modifier, prm_desc.description_html)
    m = re.match(patt, cfmt); l = int(m.group(1))
    default = "' '*%d" % l
    prm_type = 'float'
    eval_str = 'trans.prms[\'%s\'].%s' % (prm_name, suffix)
    output_field = OutputField(name=name, name_html=name_html,
        cfmt=cfmt, ffmt=ffmt, desc=desc, desc_html=desc_html,
        default=default, prm_type=prm_type, eval_str=eval_str)
    output_field.save()
    
