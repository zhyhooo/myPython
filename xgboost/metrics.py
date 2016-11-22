# -*- coding: utf-8 -*-
import os, sys
from collections import defaultdict



def precision_model( filename, topk=4 ):
    dic = {}
    for line in open(filename, 'r'):
        segs = line.strip().split('\t')
        if not dic.has_key(segs[1]):
            tmp = []
            tmp.append((int(segs[0]), segs[2], float(segs[3])))
            dic[segs[1]] = tmp 
        else:
            tmp = dic[segs[1]]
            tmp.append((int(segs[0]), segs[2], float(segs[3])))
    prec = 0.0 
    for k,v in dic.iteritems():
        hit = 0.0 
        idx = 0 
        for tpl in sorted(v, key=lambda item:item[2], reverse=True):
            if tpl[0] >= 2:
                hit += 1.0 
            idx += 1
            if idx >= topk:
                break
        #if idx < 4:
        #    print v
        if idx <= 0:
            return -1
        else:
            prec += hit/idx; 
        #print hit, idx
    #print len(dic)
    #print prec
    return prec/len(dic)

if __name__ == "__main__":
    filename = sys.argv[1]
    mapk = precision_model( filename )
    print mapk
