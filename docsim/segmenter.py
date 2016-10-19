# -*- coding: utf-8 -*-
import os, sys
import jieba
from utils import get_config_store

reload(sys)
sys.setdefaultencoding("utf-8")


class Segmenter(object):

    def __init__(self):
        '''
	load configuration
	'''
        self.segmenter = jieba 

	config  = get_config_store()
	self.cut_all = config.get("segment", "cut_all")
	self.HMM     = config.get("segment", "HMM")
	
	customized_dict = config.get("segment", "customized_dict")
        if customized_dict:
	    self.load_dict(customized_dict)

	self.stopwords = set()
	stopword_file  = config.get("segment", "stopword")
	if stopword_file:
            self.load_stopwords( stopword_file )
        

    def load_dict( self, filename ):
        '''
	load customized dictionary
	'''
        if not os.path.isfile( filename ):
            sys.stderr.write( "cannot find dictionary %s." %filename )
            return
	self.segmenter.load_userdict( filename )

    def load_stopwords( self, filename ):
        '''
	remove the stopwords 
	'''
        if not os.path.isfile( filename ):
            sys.stderr.write( "cannot find file: %s." %filename )
            return
	fin = open(filename, 'r')
	stopwords = []
	for line in fin:
            if line.startswith('#'):
	        continue
	    stopwords.append( line.strip() )
	self.stopwords = set(stopwords)

    
    def cut_line( self, input_line, cut_all=False ):
        '''
        just cut a single line, and return a list of tokens
        '''
        seg_list = self.segmenter.cut( input_line, cut_all=cut_all )
	seg_list = [ x.encode('utf-8') for x in seg_list ]
        tokens = [ x for x in seg_list if x.strip() and not x in self.stopwords ]
	return tokens


    def cut_one_file( self, filename, cut_all=False ):
        '''
        cut all sentence in a file and return a list of lists
        '''
        if not os.path.isfile( filename ):
            sys.stderr.write( "%s doesn't exist." %filename )
        fin = open( filename, 'r' )
        doc = []
        for line in fin:
            seg_list = cut_line( line, cut_all )
            if seg_list:
	        doc.append( seg_list )
        return doc

    def cut_files( self, file_list ):
        '''
        cut documents in a list of files and merge results to a list of lists
        '''
        docs = []
        for filename in file_list:
            doc = cut_one_file( filename, self.cut_all )
            docs.extends( doc )
        return docs

    def cut_folder(self, path ):
        '''
	cut all documents in the folder
	'''
	if not os.path.isdir( path ):
	     sys.stderr.write( "%s doesn't exist." %path )
	docs = []
	for filename in os.listdir( path ):
            doc = cut_one_file( filename, self.cut_all )
            docs.extends( doc )
        return docs
	    
