# -*- coding: utf-8 -*-
# Module:        barcode_upload.py
# Author:        Raks Raja - Development Team
# Description:   This module is used to upload the barcodes from current directory to S3 bucket
# Copyrights:    2020 (c) All Rights Reserved

# Python libraries
from os import listdir
from os.path import isfile, join
import logging
import boto3
from botocore.client import Config

from constant import Constant # inheriting Constant class

# Logger Config
logger = logging.getLogger(__name__)

class BarcodeUpload:

    def upload(barcode):
        """Uploads the barcodes from current directory to S3 bucket"""
        filename = "./barcodes/" + barcode
        data = open(filename, 'rb')
        s3_upload = boto3.resource('s3', config=Config(signature_version='s3v4'))
        s3_upload.Bucket(Constant.S3_BUCKET_NAME).put_object(Key=barcode, Body=data)

    barcodes = [f for f in listdir("./barcodes") if isfile(join("./barcodes", f))] # loads all the barcodes images from current barcodes directory
    for barcode in barcodes:
        upload(barcode)
    logger.info('Barcodes uploaded successfully to the S3 bucket')



