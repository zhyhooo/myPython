import os, sys
from utils import get_config_store
from gensim import corpora, models, similarities

class Model( object ):
    
    def __init__(self):
        config = get_config_store()
	
	method = config.get("method", "model")
        self.model = 
