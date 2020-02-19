# -*- coding: utf-8 -*-
# Module:        barcode_scanner.py
# Author:        Raks Raja - Development Team
# Description:   This module is used to process the barcodes in the S3 bucket.
# Copyrights:    2020 (c) All Rights Reserved.

# Python libraries
import requests
import itertools
import re
import logging
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
    for item_file in item_files:
        item_id = re.findall('\d+', item_file)
        item_ids.append(item_id)
    item_ids = list(itertools.chain.from_iterable(item_ids))

    print (location_ids)
    print (item_ids)

    # def get_category_id(key):
    #     url = base_url + 'v2/inventory_items/%s/inventory_item_lines' % (int(item_id[0]))
    #     location_definition_request = requests.get(url, headers=headers)
    #     json = location_definition_request.json()
    #     item_category_ids = []
    #     for value in json['data']:
    #         item_category_id = value.get('id', False)
    #         item_category_ids.append(item_category_id)
    #         category_url = base_url + 'v2/inventory_item_lines/%s/inventory_audit_lines' % (item_category_id)
    #         categorty_definition_request = requests.get(category_url, headers=headers)
    #         category_json = categorty_definition_request.json()
    #         description = category_json['data'][1].get('description', False)
    #         check_in_out_url = base_url + 'v2/inventory_item_lines/%s' % (item_category_id)
    #         if 'checked in' in description or 'Item placed ' in description:
    #             check_in_out_url_definition_request = requests.patch(check_in_out_url, {"checked_out": False},  headers=headers)
    #         else:
    #             check_in_out_url_definition_request = requests.patch(check_in_out_url, {"checked_out": True},headers=headers)
    #
    #     return item_category_ids

    # category_ids = []
    # for item_id in item_ids:
    #     category_id = get_category_id(item_id)
    #     category_ids.append(category_id)


