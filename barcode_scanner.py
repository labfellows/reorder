# -*- coding: utf-8 -*-
# Module:        barcode_scanner.py
# Author:        Raks Raja - Development Team
# Description:   This module is used to process the barcodes in the S3 bucket and updates the loaction IDs and the status of item line IDs
# Copyrights:    2020 (c) All Rights Reserved

# Python libraries
import requests
import itertools
import re
import json
import random
import boto3
from boto3.session import Session

from constant import Constant #Inheriting Constant class

# S3 bucket connection params
session = Session()
s3 = session.resource('s3')
s3_bucket = s3.Bucket(Constant.S3_BUCKET_NAME)


class BarcodeScanner:

    def update_item_line_status(item_line_id, location_id):
        """Scans the item line and updates the location id and checked in, checked out status """
        try:
            check_in_check_out_url = Constant.BASE_URL + 'v2/inventory_item_lines/%s' % (item_line_id)
            location_url = Constant.BASE_URL + 'v2/inventory_item_lines/%s' % (item_line_id)
            location_definition_request = requests.get(location_url, headers=Constant.headers)
            if location_definition_request.status_code != 200:
                print('An exception has occured while processing the API request for the item line ID%s: %s %s' % (item_line_id, location_definition_request.status_code, location_definition_request.reason))
                return
            location_json = location_definition_request.json()
            previous_location_id = location_json['location']['id']
            check_in_check_out_status_finder_url = Constant.BASE_URL + 'v2/inventory_item_lines?line_id=%s' % (item_line_id)
            check_in_check_out_status_definition_request = requests.get(check_in_check_out_status_finder_url, headers=Constant.headers)
            if check_in_check_out_status_definition_request.status_code != 200:
                print('An exception has occured while processing the API request for the item line ID %s: %s %s' % (item_line_id, check_in_check_out_status_definition_request.status_code, check_in_check_out_status_definition_request.reason))
                return
            check_in_check_out_status_response = check_in_check_out_status_definition_request.json()
            if location_id == previous_location_id:
                if check_in_check_out_status_response['checked_out']:
                    value = False
                    status = 'checked-in'
                else:
                    value = True
                    status = 'checked-out'
            else:
                value = False
                status = 'checked-in'
            param = json.dumps({
                "checked_out": value,
                "location_id": location_id
            })
            requests.patch(check_in_check_out_url, data=param, headers=Constant.headers) #updates the loaction id and check in, check out status through api
            print('The item line ID ' + str(item_line_id) + ' has been ' + str(status) + ' for the location ID '+ str(location_id))
        except Exception as exception:
            print('An exception has occured: ' + str(exception))

    files = []
    barcode_urls = []
    for s3_file in s3_bucket.objects.all():
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
    print('Location IDs: ' + str(location_ids))
    print('Item IDs: ' + str(item_ids))
    print('Item line IDs: ' + str(item_line_ids))

    if len(files) >= 100:
        files = files[:100]

    current_location_id = False
    for file in files:
        if 'LOC' in file:
            current_location_id = int(re.findall('\d+', file)[0])
            location_url = Constant.BASE_URL + 'v2/locations/%s' % (current_location_id)
            location_definition_request = requests.get(location_url, headers=Constant.headers)
            if location_definition_request.status_code != 200:
                print(('An exception has occured while processing the Location ID  %s: %s %s' % (current_location_id, location_definition_request.status_code, location_definition_request.reason)))
            print('Current Location ID: ' + str(current_location_id))
            continue
        if 'INV' in file:
            if not current_location_id:
                continue
            item_line_id = int(re.findall('\d+', file)[1])
            update_item_line_status(item_line_id, current_location_id)