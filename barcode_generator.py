# -*- coding: utf-8 -*-
# Module:        barcode_generator.py
# Author:        Raks Raja - Development Team
# Description:   This module is used to generate barcodes for all the items and locations available in the inventory
# Copyrights:    2020 (c) All Rights Reserved

# Python libraries
import barcode
import logging
from barcode.writer import ImageWriter

from inventory_item import InventoryItem #Inheriting LFInventory class

# Logger Config
logger = logging.getLogger(__name__)

location_ids = InventoryItem.location_ids
item_ids = InventoryItem.item_ids
item_line_ids = InventoryItem.item_line_ids

class BarcodeGenerator:

    def generate_barcode(barcode_value, id, item_line_id,  key):
        """Generates barcode with 13 digit number for each item and location ids and store them in the current barcodes directory"""
        EAN = barcode.get_barcode_class('code128')
        image = EAN(barcode_value, writer=ImageWriter()) # converts the barcode image from *.svg to *.png
        if item_line_id:
            image.save(f'./barcodes/{key}-{id}-{item_line_id}')
        else:
            image.save(f'./barcodes/{key}-{id}')

    for location_id in location_ids:
        location_format = 'L000000000000'
        barcode_value = location_format[:len(location_format) - len(str(location_id))] + str(location_id)
        generate_barcode(barcode_value, location_id, False, 'LOC')
    print('Location barcodes uploaded successfully to the barcodes folder')

    for item_line_id_dict in item_line_ids:
        item_format = 'I000000000000'
        for item_line in list(item_line_id_dict.values())[0]:
            item_id = list(item_line_id_dict.keys())[0]
            barcode_value = item_format[:len(item_format) - len(str(item_line))] + str(item_line)
            generate_barcode(barcode_value, item_id, item_line, 'INV')
    print('Item line barcodes uploaded successfully to the barcodes folder')