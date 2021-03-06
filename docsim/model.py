import os, sys
from utils import get_config_store
from segmenter import Segmenter
from gensim import corpora, models, similarities

class Model( object ):
    
    MODEL = { "bow":bow, "lsi":lsi }

    def __init__(self):
        self.config = get_config_store()
        self.dictionary = Null
	    train_set = config.get("path", "train_dir")
        __initData( train_set )

        method = config.get("model", "method")
        func = MODEL[method] 
        self.model = func

    def __initData( self, path ):
        seger = Segmenter
        corpus = seger.cut_folder( path )
        if corpus:
            self.dictionary = corpora.Dictionary( corpus )

    def doc2vec( self, doc ):
        vec = self.dictionary.doc2bow( doc.split() )
        return vec
      
    def docsim( self, doc1, doc2 ):
        vec1 = doc2vec( doc1 )
	vec2 = doc2vec( doc2 )
