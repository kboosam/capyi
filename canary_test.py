# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 15:24:56 2018

@author: kboosam
"""
'''
@@ APIs TO process the webviews from Capyi robot...

'''
# Importing libraries

#import pandas as pd
from flask import Flask, jsonify, request
import logging
from flask_cors import CORS
#import numpy as np
from raven.contrib.flask import Sentry ## Sentry logging 
#import requests
import json
import http.client
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
import io
import re, os
from random import randint
import urllib.request as req
import requests

### TEST INPUT DATA FOR RETRIEVING PROPERTY DETAILS ###
address_str = '558 mascow st'
zip_cd = '94112'
####




hc_api_key= 'G88QIR0OFHO2P4LTNBBK'
hc_api_secret= '4ERGy5KE8e7q5O9yxTB7XbHWMFqTdUfi'


canary_URL = 'https://api.housecanary.com/v2/property/details_enhanced'

params = {'address': address_str,
          'zipcode': zip_cd}

canary_resp = requests.get(canary_URL, params=params, auth=(hc_api_key, hc_api_secret))

prop = canary_resp.json()

prop = prop[0]['property/details_enhanced']['result']['public_record']
bathno = prop['number_of_bathrooms']
BRno = prop['number_of_bedrooms']
area = prop['building_area_sq_ft']
proptype = prop['property_type']
propyr = prop['year_built']





quote_text = 'We have a quote ready for your ' +  str(BRno) +' bed-' + str(bathno) + ' bath ' + proptype + ' house, built in ' + str(propyr) + ' covering '+ str(area) + 'sq.ft.'







