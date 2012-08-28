#!/usr/bin/env python
# set_collection_fields.py
import os
import sys

from pyHAWKS_config import SETTINGS_PATH
# Django needs to know where to find the HITRAN project's settings.py:
sys.path.append(SETTINGS_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from hitranmeta.models import OutputCollection, OutputField, OutputFieldOrder

collection_file = sys.argv[1]
collection_name = os.path.splitext(os.path.basename(collection_file))[0]
print 'OutputCollection name:', collection_name
output_collection = OutputCollection.objects.all().filter(
                                name=collection_name).get()

fi = open(collection_file, 'r')
field_ids = []
for line in fi.readlines():
    line = line.strip()
    if not line or line[0] == '#':
        continue
    try:
        output_field = OutputField.objects.all().filter(name=line).get()
    except OutputField.DoesNotExist:
        print 'OutputField not found: %s' % line
        sys.exit(1)
    field_ids.append(output_field.id)
fi.close()

for i, field_id in enumerate(field_ids):
    output_field_order = OutputFieldOrder(output_field_id=field_id,
                output_collection_id=output_collection.id, position = i+1)
    output_field_order.save()

