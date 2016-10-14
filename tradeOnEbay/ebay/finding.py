import sys,urllib2
from xml.etree import ElementTree as ET
from utils import get_config_store, add_elem

def findItemsByKeywords(
    keywords, affiliate=None,
    buyerPostalCode=None, paginationInput=None,
    sortOrder=None, aspectFilter=None,
    domainFilter=None, itemFilter=None,
    outputSelector=None, encoding="JSON"):
    root = ET.Element("findItemsByKeywords",
                xmlns="http://www.ebay.com/marketplace/search/v1/services")

    keywords_elem = add_elem(root, "keywords", keywords)

    if affiliate:
        affiliate_elem = add_elem(root, "affiliate")
        for key in affiliate:
            key_elem = add_elem(affiliate_elem, key, affiliate[key])

    if buyerPostalCode:
        buyPostalCode_elem = add_elem(root, "buyerPostalCode", buyerPostalCode)

    if paginationInput:
        paginationInput_elem = add_elem(root, "paginationInput")
        for key in paginationInput:
            key_elem = add_elem(paginationInput_elem, key, paginationInput[key])

    # a list of dict
    if itemFilter:
        for item in itemFilter:
            itemFilter_elem = add_elem(root, "itemFilter")
            for key in item:
                key_elem = add_elem(itemFilter_elem, key, item[key])

    if sortOrder:
        sortOrder_elem = add_elem(root, "sortOrder", sortOrder)

    # a list of dict
    if aspectFilter:
        for subDict in aspectFilter:
            aspectFilter_elem = add_elem(root, "aspectFilter")
            for key in subDict:
                key_elem = add_elem(aspectFilter_elem, key, item[key])

    # a list of Dict
    if domainFilter:
        for subDict in domainFilter:
            domainFilter_elem = add_elem(root, "domianFilter")
            for key in subDict:
                key_elem = add_elem(domainFilter_elem, key, item[key])

    if outputSelector:
        for item in outputSelector:
            outputSelector_elem = add_elem(root, "outputSelector", item)

    tree = ET.ElementTree(root)
    request = ET.dump(tree)
    return get_response(findItemsByKeywords.__name__, request, encoding)

def get_response(operation_name, data, encoding, **headers):
    config = get_config_store()
    print config
    app_name = config.get("keys", "app_name")
    globalID = config.get("call", "global_id")
    endpoint = config.get("endpoints", "finding")

    http_headers = {
        "X-EBAY-SOA-OPERATION-NAME": operation_name,
        "X-EBAY-SOA-SECURITY-APPNAME": app_name,
        "X-EBAY-SOA-GLOBAL-ID": globalID,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": encoding}

    http_headers.update(headers)

    req = urllib2.Request(endpoint, data, http_headers)
    res = urllib2.urlopen(req)
    return res.read()
    
