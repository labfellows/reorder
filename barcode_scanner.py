# -*- coding: utf-8 -*-
# Module:        barcode_scanner.py
# Author:        Raks Raja - Development Team
# Description:   This module is used to process the barcodes in the S3 bucket and updates the loaction IDs and the status of item line IDs
# Copyrights:    2020 (c) All Rights Reserved

# Python libraries
import requests
import itertools
import re
import logging
import json
import boto3
from boto3.session import Session

from constant import Constant #Inheriting Constant class

# Logger Config
logger = logging.getLogger(__name__)

# S3 bucket connection params
session = Session()
s3 = session.resource('s3')
your_bucket = s3.Bucket('lf-scripting-examples')

class BarcodeScanner:

    files = []
    barcode_urls = []
    for s3_file in your_bucket.objects.all():
        files.append(s3_file.key)
        barcode_urls.append(Constant.BASE_S3_URl + s3_file.key)

    location_files = [idx for idx in files if idx[0].lower() == 'L'.lower()]
    location_ids = []
    for location_file in location_files:
        location_id = re.findall('\d+', location_file)
        location_ids.append(location_id)
    location_ids = list(itertools.chain.from_iterable(location_ids))


    item_files = [idx for idx in files if idx[0].lower() == 'I'.lower()]
    item_ids = []
    item_line_ids = []
    for item_file in item_files:
        id = re.findall('\d+', item_file)
        item_ids.append(id[0])
        item_line_ids.append(id[1])
    item_ids = list(dict.fromkeys(item_ids))

    print (location_ids)
    print (item_ids)
    print(item_line_ids)

    def get_item_line_id(item_line_id, location_id):
        """Scans the item line and updates the location id and checked in, checked out status """
        check_in_out_url = Constant.BASE_URL + 'v2/inventory_item_lines/%s' % (item_line_id)
        category_url = Constant.BASE_URL + 'v2/inventory_item_lines/%s/inventory_audit_lines' % (item_line_id)
        categorty_definition_request = requests.get(category_url, headers=Constant.headers)
        response_json = categorty_definition_request.json()
        description_list = [sub['description'] for sub in response_json['data']]
        for description in description_list:
            if 'checked in' in description or 'Item placed ' in description:
                data = json.dumps({
                    "checked_out": True,
                    "checked_in": False,
                    "location_id":location_id
                })
                requests.patch(check_in_out_url, data=data,  headers=Constant.headers) #update the location id and check-in/checkout status
                continue
            if 'checked out' in description:
                data = json.dumps({
                    "checked_in": True,
                    "checked_out": False,
                    "location_id": location_id
                })
                requests.patch(check_in_out_url, data=data,headers=Constant.headers) ##update the location id and check-in/checkout status
                continue
        logger.info('Location ID and status has been updated successfully for the item line ' + str(item_line_id))

    location_id_list = [1, 14, 243, 245, 246]

    item_line_id_list1 = item_line_ids[:5]
    item_line_id_list2 = item_line_ids[10:15]
    item_line_id_list2 = item_line_ids[15:20]
    item_line_id_list2 = item_line_ids[20:25]
    item_line_id_list2 = item_line_ids[25:30]

    for location_id in location_id_list:
        for item_line_id in item_line_id_list1:
            get_item_line_id(item_line_id, location_id)