import sys, time
import pandas as pd
import numpy as np
from ConfigParser import ConfigParser
from os.path import isfile, join, dirname, abspath


CONFIG = None

def tictoc( message ):
    print "%s --- %s" %(time.ctime(), message)

def relative(*paths):
    return join(dirname(abspath(__file__)), *paths)

def set_config_file(filename):
    '''
    Load configuration from external file
    '''
    global CONFIG
    CONFIG = ConfigParser()
    CONFIG.read(filename)


def get_config_store():
    '''
    Return storage object with configuration values.
    '''
    global CONFIG
    if CONFIG is None:
        CONFIG = ConfigParser()
        CONFIG.read(relative("default.cfg"))
    return CONFIG


def load_trainset( filename, schema, whitelist, chunksize=50000 ):
    if not isfile( filename ):
        print "%s is not a valid filename..." %filename
    else:
        config = get_config_store()
        order_weight = float(config.get("model", "order_weight"))
        click_weight = float(config.get("model", "click_weight"))

        xtrain = np.array([]).reshape(0, len(whitelist))
        action, weight = [], []
        for chunk in pd.read_csv(filename, chunksize=chunksize, 
                                 header=None, names=schema, sep='\t'):
            chunk.replace( '\N', -1, inplace=True )
            chunk.fillna( -1, inplace=True )
            action += [ x for x in (chunk['action']>0).astype(int) ]
            weight += [ order_weight if (x==2 or x==5) else (click_weight if x==1 else 1.0) for x in chunk['action'] ]
            chunk = chunk.as_matrix(columns=whitelist)
            xtrain = np.vstack((xtrain, chunk))
        return xtrain, action, weight

def load_testset( filename, schema, whitelist, chunksize=50000 ):
    if not isfile( filename ):
        print "%s is not a valid filename..." %filename
    else:
        xtrain = np.array([]).reshape(0, len(whitelist))
        action, sid, pos = [], [], []
        for chunk in pd.read_csv(filename, chunksize=chunksize, 
                                 header=None, names=schema, sep='\t'):
            chunk.replace( '\N', -1, inplace=True )
            chunk.fillna( -1, inplace=True )
            action += list(chunk['action'])
            pos    += list(chunk['pos'])
            sid    += list(chunk['sid'])
            chunk = chunk.as_matrix(columns=whitelist)
            xtrain = np.vstack((xtrain, chunk))
        return xtrain, sid, action, pos

