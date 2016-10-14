import urllib2
from lxml import etree

from utils import get_config_store

def findItemsByKeywords(
    keywords, affiliate=None,
    buyerPostalCode=None, paginationInput=None,
    sortOrder=None, aspectFilter=None,
    domainFilter=None, itemFilter=None,
    outputSelector=None, encoding="JSON"):
    root = etree.Element("findItemsByKeywords",
                xmlns="http://www.ebay.com/marketplace/search/v1/services")

    keywords_elem = etree.SubElement(root, "keywords")
    keywords_elem.text = keywords

    if affiliate:
        affiliate_elem = etree.SubElement(root, "affiliate")
        for key in affiliate:
            key_elem = etree.SubElement(affiliate_elem, key)
            key_elem.text = affiliate[key]

    if buyerPostalCode:
        buyPostalCode_elem = etree.SubElement(root, "buyerPostalCode")
        buyerPostalCode_elem.text = buyerPostalCode

    if paginationInput:
        paginationTnput_elem = etree.SubElement(root, "paginationInput")
        for key in paginationInput:
            key_elem = etree.SubElement(paginationInput_elem, key)
            key_elem.text = paginationInput[key]

    # a list of dict
    if itemFilter:
        for item in itemFilter:
            itemFilter_elem = etree.SubElement(root, "itemFilter")
            for key in item:
                key_elem = etree.SubElement(itemFilter_elem, key)
                key_elem.text = item[key]

    if sortOrder:
        sortOrder_elem = etree.SubElement(root, "sortOrder")
        sortOrder_elem.text = sortOrder

    # a list of dict
    for subDict in aspectFilter:
        aspectFilter_elem = etree.SubElement(root, "aspectFilter")
        for key in subDict:
            key_elem = etree.SubElement( aspectFilter_elem, key)
            key_elem.text = item[key]

    # a list of Dict
    for subDict in domainFilter:
        domainFilter_elem = etree.SubElement(root, "domianFilter")
        for key in subDict:
            key_elem = etree.SubElement(domainFilter_elem, key)
            key_elem.text = item[key]

    for item in outputSelector:
        outputSelector_elem = etree.SubElement(root, "outputSelector")
        outputSelector_elem.text = item

    request = etree.tostring(root, pretty_print=True)
    return get_response(findItemsByKeywords.__name__, request, encoding)

def get_response(operation_name, data, encoding, **headers):
    config = get_config_store()
    globalID = config.get("call", "globalid")
    app_name = config.get("keys", "app_name")
    endpoint = config.get("endpoints", "finding")

    http_headers = {
        "X-EBAY-SOA-OPERATION-NAME": operation_name,
        "X-EBAY-SOA-SECURITY-APPNAME": app_name,
        "X-EBAY-SOA-GLOBAL-ID": globalId,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": encoding}

    http_headers.update(headers)

    req = urllib2.Request(endpoint, data, http_headers)
    res = urllib2.urlopen(req)
    return res.read()
    
