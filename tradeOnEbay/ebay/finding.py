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
