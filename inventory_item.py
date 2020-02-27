# -*- coding: utf-8 -*-
# Module:       inventory_item.py
# Author:       Raks Raja  -  Development Team
# Description:  This file is used to get the available location and item IDs from the inventory
# Copyrights:   2020 (c) All Rights Reserved

# Python libraries
from constant import Constant # inheriting LFConstants class
import requests
import logging

# Logger Config
logger = logging.getLogger(__name__)

class InventoryItem:

    def get_item_and_location_ids(key):
        """ To get location and item ids from the inventory"""
        url = Constant.BASE_URL + 'v2/' + key
        request = requests.get(url, headers = Constant.headers)
        response_json = request.json()
        ids = []
        for value in response_json['data']:
            ids.append(value.get('id', False))
        return ids

    def get_item_line_ids(id):
        """ To get item line ids from the inventory"""
        url = Constant.BASE_URL + 'v2/inventory_items/%s/inventory_item_lines' % (id)
        request = requests.get(url, headers = Constant.headers)
        response_json = request.json()
        item_line_ids = []
        for value in response_json['data']:
            item_line_ids.append(value.get('id', False))
        return {id: item_line_ids}

    location_ids = get_item_and_location_ids('locations')
    item_ids = get_item_and_location_ids('inventory_items')
    item_line_ids = []
    for item_id in item_ids:
        item_line_id = get_item_line_ids(item_id)
        item_line_ids.append(item_line_id)

    print('Location IDS: ' + str(location_ids))
    print('Item IDS: ' + str(item_ids))
    print('Item Line IDS: ' + str(item_line_ids))