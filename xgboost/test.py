# -*- coding: utf-8 -*-
import sys, os, time
import numpy as np
import xgboost as xgb
from utils import load_testset, tictoc, set_config_file, get_config_store
from metrics import precision_model


if __name__ == '__main__':

    tictoc("start...")
    config_filename = sys.argv[1]
    set_config_file( config_filename )
    config       = get_config_store()
    filename     = config.get("path", "test_filename")
    model_path   = config.get("path", "model_path")
    score_path   = config.get("path", "score_path")
    missing      = float(config.get("model", "missing"))

    schema       = config.get("schema", "columns").translate(None,' \n').split(',')
    feature      = config.get("schema", "selected").translate(None,' \n').split(',')

    ###########   Load Model File  ##############
    tictoc("load data...")
    bst = xgb.Booster(model_file=model_path)
    xtest, sid, action, pos, sku = load_testset( filename, schema, feature )

    ######### Scoring ###############
    tictoc("predict...")
    dtest = xgb.DMatrix(xtest, missing=missing)
    Y_test=bst.predict(dtest)

    ########  Result  ###############
    out = open(score_path,'w')
    assert len(sid)==len(Y_test) and len(pos)==len(Y_test) and len(action)==len(Y_test)

    for i in range(len(Y_test)):
        out.write( "%s\t%s\t%s\t%.8f\t%s\n" %(action[i], sid[i], pos[i], Y_test[i], sku[i])

    tictoc("calculate map@k")
    print score_path
    mapk = precision_model( score_path, 4 ) 
    print "average precision @4 is %.6f" %mapk
