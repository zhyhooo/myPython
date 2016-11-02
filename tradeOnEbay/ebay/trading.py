#-*- coding: utf-8 -*-
import sys
from xml.dom.minidom import parseString

from utils import get_endpoint_response, get_endpoint_response_with_file,
                  get_config_store, add_elem
from xml.etree import ElementTree as ET
                    

def addItemWithPic( image, **kwargs ):
    url = uploadSiteHostedPicture(image)
    kwargs['pictureDetails'] = [url]
    return addItem(**kwargs)

def addItem( title, description, primaryCategoryId, startPrice='0.99',
             buyItNowPrice=None, country='US', currency='USD', 
	         dispatchTimeMax='3', listingDuration='Days_7',
	         listingType='Chinese', paymentMethods=['Paypal'],
	         paypalEmailAddress='', pictureDetails=[], postalCode='',
	         photoDisplay='PicturePack', condition='new', returnPolicy={}
	         quantity=1, freeShipping=False, site='US', test=False ):
    
    # get the user auth token
    token = get_config_store().get("auth", "token")
    oname = "AddItem" if not test else 'VerifyAddItem'
    rname = "%sRequest" % oname
    root = ET.Element(rname, xmlns="urn:ebay:apis:eBLBaseComponents")

    # add to xml 
    credentials_elem = add_elem(root, "RequesterCredentials")
    token_elem = add_elem(credentials_elem, "eBayAuthToken", token)

    item_elem = add_elem(root, "Item")
    
    title_elem        = add_elem(item_elem, "Title", title)
    desc_elem         = add_elem(item_elem, "Description", description)
    primary_cate_elem = add_elem(item_elem, "PrimaryCategory")
    cid_elem          = add_elem(primary_cate_elem, "CategoryID", primaryCategoryId)
    condition_elem    = add_elem(item_elem, "ConditionID", CID.get(condition, '1000'))
    init_price_elem   = add_elem(item_elem, "StartPrice", startPrice)
    if buyItNowPrice:
        buyNow_price_elem = add_elem(item_elem, "BuyItNowPrice", buyItNowPrice)
    
    cma_elem          = add_elem(item_elem, "CategoryMappingAllowed", 'true')
    country_elem      = add_elem(item_elem, "Country", country)
    currency_elem     = add_elem(item_elem, "Currency", currency)
    dtm_elem          = add_elem(item_elem, "DispatchTimeMax", dispatchTimeMax)
    ld_elem           = add_elem(item_elem, "ListingDuration", listingDuration)
    for t in paymentMethods:
        pm_elem = add_elem(item_elem, "PaymentMethods", t)
    ppea_elem         = add_elem(item_elem, "PayPalEmailAddress", payPalEmailAddress)
    pdt_elem          = add_elem(item_elem, "PictureDetails", None)
    pdp_elem          = add_elem(item_elem, "PhotoDisplay", photoDisplay)
    for url in pictureDetails:
        purl_elem = add_elem(pdt_elem, "PictureURL", url)
    pc_elem           = add_elem(item_elem, "PostalCode", postalCode)
    qt_elem           = add_elem(item_elem, "Quantity", quantity)

    # default return
    returnPol_elem = add_e(item_e, "ReturnPolicy")
    add_elem(returnPol_elem, "ReturnsAcceptedOption", returnPolicy.get("accept","ReturnsAccepted"))
    add_elem(returnPol_elem, "RefundOption", returnPolicy.get("option","MoneyBack"))
    add_elem(returnPol_elem, "ReturnsWithinOption", returnPolicy.get("delay","Days_30"))
    add_elem(returnPol_elem, "Description", returnPolicy.get("desc",""))
    add_elem(returnPol_elem, "ShippingCostPaidByOption", returnPolicy.get("payer","Buyer"))
    # end default ret pol

    sd_elem           = add_elem(item_elem, "ShippingDetails", None)
    if freeShipping:
        pass
    site_elem         = add_elem(item_elem, "Site", site)

    request = ET.tostring(root, 'utf-8')
    return get_response(oname, request)
   
def getCategories( parentId=None, detailLevel='ReturnAll', errorLanguage=None,
                   messageId=None, outputSelector=None, version=None, levelLimit=1,
		   warningLevel="High", viewAllNodes=True, categorySiteId=0,
		   encoding="JSON"):
    '''
    based on http://developer.ebay.com/DevZone/XML/docs/Reference/eBay/GetCategories.html#Request
    '''
    # get user auth token
    token = get_config_store().get("auth", "token")
    root = ET.Element(rname, xmlns="urn:ebay:apis:eBLBaseComponents")
    #add it to the xml doc
    credentials_elem = add_elem(root, "RequesterCredentials")
    token_elem       = add_elem(credentials_elem, "eBayAuthToken", token)

    if parentId == None and levelLimit:
        levelLimit_elem = add_elem(root, "LevelLimit", levelLimit)
    elif parentId:
        parentId_elem   = add_elem(root, "CategoryParent", parentId)

    viewAllNodes_elem   = add_elem(root, "ViewAllNodes", viewAllNodes.lower())
    categorySiteId_elem = add_elem(root, "CategorySiteID", categorySiteId)
    if detailLevel:
        add_elem(root, "DetailLevel", detailLevel)
    if errorLanguage:
        add_elem(root, "ErrorLanguage", errorLanguage)
    if messageId:
        add_elem(root, "MessageID", messageId)
    if outputSelector:
        add_elem(root, "OutputSelector", outputSelector)
    if version:
        add_elem(root, "Version", version)
    if warningLevel:
        add_elem(root, "WarningLevel", warningLevel)




def get_response( operation_name, data, encoding="utf-8", **headers ):
    return get_endpoint_response( "trading", operation_name, data, encoding, **headers )

def get_response_with_file( operation_name, fobj, data, encoding="utf-8", **headers ):
    return get_endpoint_response_with_file( "trading", operation_name, fobj, data, encoding, **headers ) 
