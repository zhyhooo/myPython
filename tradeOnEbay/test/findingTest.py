import sys
sys.path.append('..')
from ebay.finding import findItemsByKeywords

print findItemsByKeywords(keywords='iphone', encoding='XML',
                          paginationInput = {'entriesPerPage':'5',
                                             'pageNumber':'1'})
                                              
