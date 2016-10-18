import sys, os
from ConfigParser import ConfigParser
from os.path import join, dirname, abspath


CONFIG = None

def relative(*paths):
    return join(dirname(abspath(__file__)), *paths)


def set_config_file(filename):
    '''
    Load configuration from external files
    '''
    global CONFIG
    CONFIG = ConfigParser()
    CONFIG.read(filename)


def get_config_store():
    '''
    Return configuration
    '''
    global CONFIG
    if CONFIG is None:
        CONFIG = ConfigParser()
    CONFIG.read(relative("config.cfg"))
    return CONFIG
