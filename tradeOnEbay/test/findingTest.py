import sys
sys.path.append('..')
from ebay.finding import *

#print findItemsByKeywords(keywords='iphone6', encoding='XML',
#                          paginationInput = {'entriesPerPage':'5',
#                                             'pageNumber':'1'})
#print findCompletedItems(keywords='GPS Receiver', encoding='XML',
#                         categoryId='156955', itemFilter = [{'name':'FreeShippingOnly', 'value':'true'}],
#                         paginationInput = {'entriesPerPage':'5', 'pageNumber':'1'},
#                         sortOrder='PricePlusShippingLowest')                         
#print findItemsByProduct(productId = {'id':'62923188', 'attr':{"type":"ReferenceID"}},
#                         paginationInput = {'entriesPerPage':'5', 'pageNumber':'1'})
print getHistograms(categoryId=["11233"])
