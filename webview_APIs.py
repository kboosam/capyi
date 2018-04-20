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
#import json, http.client
#import urllib.request as req
from random import randint
import urllib.parse as parse
import requests

####
## FUNCTION TO CALL CANARY HOUSE API TO GET THE HOURSE DETAILS
####

def get_propdetails(address, zip_cd):


    hc_api_key= 'G88QIR0OFHO2P4LTNBBK'
    hc_api_secret= '4ERGy5KE8e7q5O9yxTB7XbHWMFqTdUfi'
    
    canary_URL = 'https://api.housecanary.com/v2/property/details_enhanced'
    
    params = {'address': address,
              'zipcode': zip_cd}
    
    try:
        canary_resp = requests.get(canary_URL, params=params, auth=(hc_api_key, hc_api_secret))
        prop = canary_resp.json()
    except Exception as e:
        print(e)
        sentry.captureMessage(message=e, level=logging.FATAL) #printing all exceptions to the log
        prop = {
                 "set_attributes": {
    							
    							"jsonAPIError": "YES"
    						},
                "messages": [
                   {"text": "An error occurred while fetching the house details -101"},
                  ]
                }
    print('--> Property details retrieved from Canary:', prop)        
    return prop
### END OF FUNCTION ####

####
## FUNCTION TO build response for quote request
####

def build_resp(prop, fbid):
    
    attributes= ''
    messages = ''
    print('---> Entered the response building process')
    try: 
        address_det = prop[0]['address_info']['address_full']
        prop = prop[0]['property/details_enhanced']['result']['public_record']
        bathno = prop['number_of_bathrooms']
        BRno = prop['number_of_bedrooms']
        area = prop['building_area_sq_ft']
        proptype = prop['property_type']
        propyr = prop['year_built']
        prop_val = prop['assessment']['total_assessed_value']
        
        if(bathno != None): # not a commercial property
        
            quote_text = 'We have a quote ready for your ' + str(BRno) + ' bed - ' + str(bathno) + ' bath ' + proptype + ' house, built in ' + str(propyr) + ' covering '+ str(area) + 'sq.ft.'
            
            attributes = {
                        'hq_address': address_det,
                        'hq_prop_val': prop_val,
                        'hq_area': area,
                        'jsonAPIError': 'NO'     
                    }
            print("---> Attributes: ", attributes)
            
            messages = [
                    {
                            'attachment': {
                                    'type': 'template',
                                    'payload': {
                                            'template_type':'button',
                                            'text': quote_text,
                                            'buttons': [
                                                    {
                                                            'type':'web_url',
                                                            'url': 'https://capyi.herokuapp.com/services/hq?fbid='+ fbid + '&builtarea='+ str(area) + '&address='+ parse.quote_plus(address_det, safe='',encoding=None, errors=None) + '&value=' + str(prop_val),
                                                            'title': 'Show me details'
                                                            },
                                                    {
                                                            'type':'show_block',
                                                            'block_names': ['Any Thing Else'],
                                                            'title': 'No, i am rich'
                                                                                                                
                                                            }
                                                    ]
                                            }
                                    }
        
                            }
                    ]
            
            resp = {
                    'set_attributes': attributes,
                    'messages': messages
                    }
        else:
            resp = {
                    'set_attributes': {
                            'jsonAPIError':'NO'
                            },
                    'messages': [ {
                            
                            'text': 'The property at this address appears to be a commercial property. Please call our customer care for Insurance options.'
                            }
                            
                            ]
                    }
    except Exception as e:
        print(e)
        sentry.captureMessage(message=e, level=logging.FATAL) #printing all exceptions to the log
        resp = {
                 "set_attributes": {
    							
    							"jsonAPIError": "YES"
    						},
                "messages": [
                   {"text": "An error occurred while building the response jSON -102"},
                  ]
                }
                 
    print("---> Response: ", resp)
    return resp
### END OF FUNCTION ####


###################################################################
app = Flask(__name__)
#set sentry for logging the messages
sentry = Sentry(app, dsn='https://e8ddaf32cc924aa295b846f4947a9332:5e52d48fe13a4d2c82babe6833c5f871@sentry.io/273115')
CORS(app) ## cross origin resource whitelisting..

## 
@app.route('/services/gethome', methods=['POST','GET'])
def get_home():
    print('--> Get home API started ******* \n\n')
    try: 
        #req = request.json
        address_str = request.args.get('delivery_line', type= str)
        zip_cd = request.args.get('zipcode', type= str)
        #fbid = request.args.get('fb_id', type= str)
        fbid='ysurance'
        print("##This is the request:", request.args , '\n\n')        
        
        #print("##This is the request JSON:", str(request.get_json()), '\n\n')
        sentry.captureMessage(message='Started processing request- {}'.format(address_str), level=logging.INFO)
        
    except Exception as e:
        print(e)
        sentry.captureMessage(message=e, level=logging.FATAL)
        resp = {
                "set_attributes": {
    							
    							"jsonAPIError": "YES"
    						},
                        
                "messages": [
                   {"text": "An error occurred while fetching the DL image details for your vehicle - 102."},
                  ]
                }
    
    ### TEST INPUT DATA FOR RETRIEVING PROPERTY DETAILS ###
    #address_str = '558 mascow st'
    #zip_cd = '94112'
    ####
    
    prop = get_propdetails(address_str, zip_cd)
    resp = build_resp(prop, fbid)
    
    return jsonify(resp)
#### END OF  function

## 
@app.route('/services/hq', methods=['POST','GET'])
def get_hq():
    
    print('--> Get home API started ******* \n\n')
    try: 
        print("##This is the request:", request.args , '\n\n')        
        #address_str = request.args.get('address', type= str)
        prop_val = request.args.get('value', type= int)
        fbid = request.args.get('fbid', type= str)
        area = request.args.get('area', type= int)
        qtnum = str(randint(100001, 199999))      ## GENERATE A RANDOM QUOTE NUMBER
        
        #print("##This is the request JSON:", str(request.get_json()), '\n\n')
        sentry.captureMessage(message='Started processing request- {}'.format(qtnum + '-' + fbid), level=logging.INFO)
        
       
    except Exception as e:
        print(e)
        sentry.captureMessage(message=e, level=logging.FATAL)
        resp = {
                "error":True,
                "msg": "Error while calculating the premium"
                }
    
    
    if prop_val <200000:
        premium = prop_val * 0.000525 
    
    elif prop_val < 350000:
        premium = prop_val * 0.000510 

    elif prop_val < 500000:
        premium = prop_val * 0.000490 
    else:
        premium = prop_val * 0.000475
    
    premium = premium * int(area)/850
    error = False
    discount = randint(20,30)
    
    resp = {
            "premium": premium,
            "discount": discount, 
            "error": error
            }
    
    print('---> Quote Response:', resp)
    
    return jsonify(resp)
#### END OF  function


# main function
if __name__ == '__main__':
   ## DISABLE CERITIFACATE VERIFICATION FOR SSL.. some issue in Capgemini network..
   '''
   try:
        _create_unverified_https_context = ssl._create_unverified_context
   except AttributeError:
         # Legacy Python that doesn't verify HTTPS certificates by default
        pass
   else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context
   '''    
   sentry.captureMessage('Started runnning API for Home Quote !!')
   #app.run(debug= True)
   app.run(debug=True,port=5100) #turnoff debug for production deployment

