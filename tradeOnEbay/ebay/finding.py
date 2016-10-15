import sys,urllib2
from xml.etree import ElementTree as ET
from utils import get_config_store, add_elem


def appendArgus( root, **kwargs ):
    for kw, arg in kwargs.items():
        # standard input fields
        if kw == "affiliate" and arg:
            affiliate_elem = add_elem(root, kw)
            for key in arg:
                key_elem = add_elem(affiliate_elem, key, arg[key])
        if kw == "buyerPostalCode" and arg:
            buyPostalCode_elem = add_elem(root, kw, arg)
        if kw == "paginationInput" and arg:
            paginationInput_elem = add_elem(root, kw)
            for key in arg:
                key_elem = add_elem(paginationInput_elem, key, arg[key])
        if kw == "sortOrder" and arg:
            sortOrder_elem = add_elem(root, kw, arg)

        # call-specific input fields
        if kw == "keywords" and arg:
            keywords_elem = add_elem(root, kw, arg)
        if kw == "categoryId" and arg:
            for category in arg[0:4]:
                category_elem = add_elem(root, kw, category)
        if kw == "storeName" and arg:
            store_elem = add_elem(root, kw, arg)
        # a list of dict
        if kw == "itemFilter" and arg:
            for subDict in arg:
                itemFilter_elem = add_elem(root, kw)
                for key in subDict:
                    key_elem = add_elem(itemFilter_elem, key, subDict[key])
        # a list of dict
        if kw == "aspectFilter" and arg:
            for subDict in arg:
                aspectFilter_elem = add_elem(root, kw)
                for key in subDict:
                    key_elem = add_elem(aspectFilter_elem, key, subDict[key])
        # a list of Dict
        if kw == "domainFilter" and arg:
            for subDict in arg:
                domainFilter_elem = add_elem(root, kw)
                for key in subDict:
                    key_elem = add_elem(domainFilter_elem, key, subDict[key])
        if kw == "outputSelector" and arg:
            for item in arg:
                outputSelector_elem = add_elem(root, kw, item)
        if kw == "productId" and arg:
            productId_elem = add_elem(root, kw, arg["id"], arg.get("attr", None) )
    return root


def findItemsByKeywords(
    keywords, affiliate=None,
    buyerPostalCode=None, paginationInput=None,
    sortOrder=None, aspectFilter=None,
    domainFilter=None, itemFilter=None,
    outputSelector=None, encoding="XML"):

    api_name = findItemsByKeywords.__name__
    root = ET.Element(api_name, xmlns="http://www.ebay.com/marketplace/search/v1/services")
    root = appendArgus( root, keywords=keywords, affiliate=affiliate,
                        buyerPostalCode=buyerPostalCode, paginationInput=paginationInput,
                        sortOrder=sortOrder, aspectFilter=aspectFilter,
                        domainFilter=domainFilter, itemFilter=itemFilter,
                        outputSelector=outputSelector)

    request = ET.tostring(root, 'utf-8')
    return get_response(api_name, request, encoding)


def findCompletedItems(
    keywords, affiliate=None, categoryId=None,
    buyerPostalCode=None, paginationInput=None,
    sortOrder=None, aspectFilter=None, productId=None,
    domainFilter=None, itemFilter=None,
    outputSelector=None, encoding="XML"):

    api_name = findCompletedItems.__name__
    root = ET.Element(api_name, xmlns="http://www.ebay.com/marketplace/search/v1/services")
    root = appendArgus( root, keywords=keywords, affiliate=affiliate,
                        buyerPostalCode=buyerPostalCode, paginationInput=paginationInput,
                        sortOrder=sortOrder, aspectFilter=aspectFilter, productId=productId,
                        domainFilter=domainFilter, itemFilter=itemFilter,
                        outputSelector=outputSelector)

    request = ET.tostring(root, 'utf-8')
    return get_response(api_name, request, encoding)

def findItemsByProduct(
    productId, affiliate=None,
    buyerPostalCode=None, paginationInput=None,
    sortOrder=None, aspectFilter=None,
    domainFilter=None, itemFilter=None,
    outputSelector=None, encoding="XML"):

    api_name = findItemsByProduct.__name__
    root = ET.Element(api_name, xmlns="http://www.ebay.com/marketplace/search/v1/services")
    root = appendArgus( root, productId=productId, affiliate=affiliate,
                        buyerPostalCode=buyerPostalCode, paginationInput=paginationInput,
                        sortOrder=sortOrder, aspectFilter=aspectFilter,
                        domainFilter=domainFilter, itemFilter=itemFilter,
                        outputSelector=outputSelector)

    request = ET.tostring(root, 'utf-8')
    return get_response(api_name, request, encoding)

def getHistograms(categoryId, encoding="XML"):
    api_name = getHistograms.__name__
    root = ET.Element(api_name, xmlns="http://www.ebay.com/marketplace/search/v1/services")
    root = appendArgus( root, categoryId=categoryId)

    request = ET.tostring(root, 'utf-8')
    return get_response(api_name, request, encoding)
    

def get_response(operation_name, data, encoding, **headers):
    config = get_config_store()
    app_name = config.get("keys", "app_name")
    globalID = config.get("call", "global_id")
    endpoint = config.get("endpoints", "finding")

    http_headers = {
        "X-EBAY-SOA-OPERATION-NAME": operation_name,
        "X-EBAY-SOA-SECURITY-APPNAME": app_name,
        "X-EBAY-SOA-GLOBAL-ID": globalID,
        "X-EBAY-SOA-RESPONSE-DATA-FORMAT": encoding}

    http_headers.update(headers)

    print data
    req = urllib2.Request(endpoint, data, http_headers)
    res = urllib2.urlopen(req)
    return res.read()
    
