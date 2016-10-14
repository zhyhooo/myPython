#-*- coding: utf-8 -*-
import sys
from xml.dom.minidom import parseString

from utils import ( get_endpoint_response, get_config_store )
from lxml import etree, objectify
                    

def addItemWithPic( image, **kwargs ):
    url = up;oadSiteHostedPicture(image)
    kwargs['pictureDetails'] = [url]
    return addItem(**kwargs)

def addItem( title, description, primaryCategoryId, startPrice='0.99',
             buyItNowPrice=None, country='US', currency='USD', 
	     dispatchTimeMax='3', listingDuration='Days_7',
	     listingType='Chinese', paymentMethods=['Paypal'],
	     paypalEmailAddress='', pictureDetails=[], postalCode='',
	     photoDisplay='PicturePack', condition='new',
	     quantity=1, freeShipping=False, site='US', test=False ):
    
    # get the user auth token
    token = get_config_store().get("auth", "token")
    oname = "AddItem" if not test else 'VerifyAddItem'
    rname = "%sRequest" % oname
    root = etree.Element(rname, xmlns="urn:ebay:apis:eBLBaseComponents")

    # add to xml 
    credentials_elem = etree.SubElement(root, "RequesterCredentials")
    token_elem = etree.SubElement(credentials_elem, "eBayAuthToken")
    token_elem.text = token

    item_elem = etree.SubElement(root, "Item")
    
    title_elem = add_elem(item_elem, "Title", title)
    desc_elem = add_elem(item_elem, "Description", description)
    primary_cate_elem = add_elem(item_elem, "PrimaryCategory")
    cid_elem = add_elem(primary_cate_elem, "CategoryID", primaryCategoryId)
    condition_elem = add_elem(item_elem, "ConditionID", CID.get(condition, '1000'))
    init_price_elem = add_elem(item_elem, "StartPrice", startPrice)
    if buyItNowPrice:
        buyNow_price_elem = add_elem(item_elem, "BuyItNowPrice", buyItNowPrice)
    
    cma_elem = 

