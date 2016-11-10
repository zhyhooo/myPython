import os, sys, time, math
import numpy as np
import xgboost as xgb
from schema import feature, schema
from utils import load_trainset, tictoc, set_config_file, get_config_store




if __name__=='__main__':
    
    config_filename = sys.argv[1]
    set_config_file( config_filename )
    config = get_config_store()
    filename     = config.get("path", "train_filename")
    model_path   = config.get("path", "model_path")
    featImp_path = config.get("path", "featImp_path")

    max_depth    = config.get("model", "max_depth")
    eta          = config.get("model", "eta")
    objective    = config.get("model", "objective")
    nthread      = config.get("model", "nthread")
    missing      = float(config.get("model", "missing"))
    nround       = int(config.get("model", "round"))

    tictoc("start...")

    tictoc("load data...")
    xtrain,action,weight = load_trainset(filename, schema, feature)
    dtrain = xgb.DMatrix(xtrain, label=action, weight=weight, missing=missing)
    
    tictoc("train model...")
    param = {'bst:max_depth':max_depth, 'eta':eta,'objective': objective, 'nthread':nthread}
    plst = param.items()
    evallist  = [ (dtrain,'train')]

    num_round = nround
    bst = xgb.train( plst, dtrain, num_round, evallist )
    bst.save_model(model_path)
    #bst.dump_model('dump.nice1.txt','featmap.txt')

    tictoc("calculate feature importance...")
    featureImpFile=open(featImp_path,'w')
    FeatImp = bst.get_fscore()
    sortFeatImp = sorted(FeatImp.iteritems(),key = lambda FeatImp:FeatImp[1], reverse = True)
    maxImp = (float)(sortFeatImp[0][1])
    for i in range(len(sortFeatImp)):
        featureImpFile.write(str(i+1) + '\t' + feature[(int)(sortFeatImp[i][0][1:])]+'\t' +str((float)(sortFeatImp[i][1])/maxImp)+'\n')

    tictoc('done...')
