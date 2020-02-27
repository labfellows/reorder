# -*- coding: utf-8 -*-
# Module:        barcode_scanner.py
# Author:        Raks Raja - Development Team
# Description:   This module is used to process the barcodes from the S3 bucket and process check-in/check-out in inventory based on the location
# Copyrights:    2020 (c) All Rights Reserved

# Python libraries
import requests
import itertools
import re
import logging
import json
import random
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

    def update_item_line_status(item_line_id, location_id):
        """Scans the item line and updates the location id and checked in, checked out status """
        check_in_check_out_url = Constant.BASE_URL + 'v2/inventory_item_lines/%s' % (item_line_id)
        identifier_url = Constant.BASE_URL + 'v2/inventory_item_lines/%s' % (item_line_id)
        identifier_definition_request = requests.get(identifier_url, headers=Constant.headers)
        identifier_json = identifier_definition_request.json()
        identifier_value = identifier_json['identifier']
        check_in_check_out_status_finder_url = Constant.BASE_URL + 'v2/inventory_item_lines?identifier=%s' % (identifier_value)
        check_in_check_out_status_definition_request = requests.get(check_in_check_out_status_finder_url, headers=Constant.headers)
        if check_in_check_out_status_definition_request.status_code == 404:
            print('Error! Unable to find the status of Identifier ' + str(identifier_value))
            return
        check_in_check_out_status_response = check_in_check_out_status_definition_request.json()
        if check_in_check_out_status_response['checked_out']:
            value = False
            status = 'checked-in'
        else:
            value = True
            status = 'checked-out'
        param = json.dumps({
            "checked_out": value,
            "location_id": location_id
        })
        requests.patch(check_in_check_out_url, data=param, headers=Constant.headers) #updates the loaction id and check in, check out status through api
        print('The item line ID ' + str(item_line_id) + ' has been ' + str(status) + ' for the location ID '+ str(location_id))



    files = []
    barcode_urls = []
    for s3_file in your_bucket.objects.all():
        files.append(s3_file.key)
        barcode_urls.append(Constant.BASE_S3_URl + s3_file.key)
    random.shuffle(files)

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
    random.shuffle(location_ids)
    random.shuffle(item_line_ids)

    if len(files) >= 100:
        files = files[:100]

    current_location_id = False
    for file in files:
        if 'LOC' in file:
            current_location_id = int(re.findall('\d+', file)[0])
            location_url = Constant.BASE_URL + 'v2/locations/%s' % (current_location_id)
            location_definition_request = requests.get(location_url, headers=Constant.headers)
            if location_definition_request.status_code == 404:
                print('Error! Location ID ' + str(current_location_id) + ' does not exists!')
            print('Current Location ID: ' + str(current_location_id))
            continue
        if 'INV' in file:
            if not current_location_id:
                continue
            item_line_id = int(re.findall('\d+', file)[1])
            update_item_line_status(item_line_id, current_location_id)