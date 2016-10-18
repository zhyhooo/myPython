#-*- coding: utf-8 -*-
import sys
from xml.dom.minidom import parseString

from utils import get_endpoint_response, get_config_store, add_elem
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
    return get_response(oname, request, encoding)
   

