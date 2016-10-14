#-*- coding: utf-8 -*-
import sys, os
import json, requests, urllib2
from ConfigParser import ConfigParser
from lxml import etree

CONFIG = None



def get_endpoint_response(endpoint_name, operation_name, data, encoding, **headers):
    config = get_config_store()
    endpoint = config.get("endpoints", endpoint_name)
    app_name = config.get("keys", "app_name")
    dev_name = config.get("keys", "dev_name")
    cert_name = config.get("keys", "cert_name")
    siteId = config.get("call", "siteid")
    compatibility_level = config.get("call", "compatibility_level")

    http_headers = {
                "X-EBAY-API-COMPATIBILITY-LEVEL": compatibility_level,
		"X-EBAY-API-DEV-NAME": dev_name,
		"X-EBAY-API-APP-NAME": app_name,
		"X-EBAY-API-CERT-NAME": cert_name,
		"X-EBAY-API-CALL-NAME": operation_name,
		"X-EBAY-API-SITEID": siteId,
		"Content-Type": "text/xml"}

    http_headers.update(headers)

    req = urllib2.Request(endpoint, data, http_headers)
    res = urllib2.urlopen(req)
    return res.read()


def set_config_file(filename):
    '''
    Load configuration from external file
    '''
    global CONFIG
    CONFIG = ConfigParser()
    CONFIG.read(filename)

def get_config_store():
    '''
    Return storage object with configuration values.
    '''
    global CONFIG
    if CONFIG is None:
        CONFIG = ConfigParser()
	CONFIG.read("./default-config.cfg")
    return CONFIG


def add_elem(parent, key, value=None):
    child = etree.SubElement(parent, key)
    if val:
        child.text = str(val)
    return child

class Value(object):
    def __init__(self,
                 number=None,
		 text=None,
		 url=None):
	self.number = number
	self.text = text
	self.url = url

