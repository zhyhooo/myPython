# http://lazyprogrammer.me/tutorial-on-collaborative-filtering-and-matrix-factorization-in-python/
import sys, os
import numpy as np
import math
import numpy.ma as ma
from numpy import inf
from time import gmtime, strftime
from scipy.sparse import coo_matrix
from collections import defaultdict

def matrix_factorization(U, V, B, C, steps=201, mu=1, reg=0.1):

    for t in xrange(steps):

        print "Step %d is doing... %s" %(t, strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    
        # update B
        accum = np.sum( np.multiply( (mat - U.dot(V) - C - mu), mask ), axis=1 )
        B = accum / (1 + reg) / (np.sum(mask, axis=1).T)
        B[B==inf] = 0
        B[np.isnan(B)] = 0

    
        # update U
        for i in xrange(M):
            if mask[[i],:].max() > 0:
                vv = np.multiply( mask[[i],:], V )
                matrix = vv.dot(vv.T) + reg*np.eye(K)
                vector = np.sum( np.multiply( (mat[[i],:] - C - B[i] - mu), vv), axis=1 )
                U[i,:] = np.linalg.solve(matrix, vector)
    
        # update C
        accum = np.sum( np.multiply( (((mat- U.dot(V)).T-B).T-mu), mask ), axis=0 )
        C = accum / (1 + reg) / (np.sum(mask, axis=0).T)
        C[C==inf] = 0
        C[np.isnan(C)] = 0

    
        # update V
        for j in xrange(N):
            if mask[:,[j]].max() > 0:
                uu = np.multiply( U, mask[:,[j]] )
                matrix = uu.T.dot(uu) + reg*np.eye(K)
                vector = np.sum( np.multiply( (mat[:,[j]] - B[:,np.newaxis] - C[j] - mu), uu), axis=0 )
                V[:,j] = np.linalg.solve(matrix, vector)


        nR = np.add( np.add( np.add( np.dot(U,V), C ), B.reshape((M, 1)) ), mu )
        error = np.sum( np.power( np.multiply((mat - nR), mask), 2) )
        print "Step %d is done... square errors: %f" %(t, error)

        if t%100==0 and t>0:
            fout = open('result01_'+str(t), 'w')
            for i in xrange(M):
                for j in xrange(N):
                    print >>fout, "%s\t%s\t%s\t%s\t%f" % (rindex[i][0], rindex[j][0], rindex[i][1], rindex[j][1], nR[i,j] )

    return U, V, B, C


def loadData(finput='cid2cid.txt'):
    mat = {}
    index = 0
    dindex = {}  # lookup table of original id
    rindex = {}  # lookup table of new index 
    max_ff = defaultdict(int)
    fin = open(finput, 'r')
    for line in fin:
        sku, sku_name, csku, csku_name, ff, rank = line.strip().split('\001')
        ff, rank = int(ff), int(rank)
        if sku in dindex:
            sku_id = dindex[sku][0]
        else:
            dindex[sku] = (index, sku_name) # c3_id, c3_name
            rindex[index] = (sku, sku_name)
            sku_id = index
            index += 1
        if csku in dindex:
            csku_id = dindex[csku][0]
        else:
            dindex[csku] = (index, csku_name)
            rindex[index] = (csku, csku_name)
            csku_id = index
            index += 1
        mat[(sku_id, csku_id)] = ff
    return mat, index, dindex, rindex


def norm(mat, method="log_minmax"):
    if method=="minmax":
        max_ff = np.amax(mat, axis=1)
        mat = mat *1.0 / max_ff[:, np.newaxis]
    elif method=="log_minmax":
        max_ff = np.amax(mat)
        mat = np.log2(mat+1) / np.log2(max_ff+1)
    mat[np.isnan(mat)] = 0
    return mat
    

## load data from disk
loadFromDisk = False
mat, max_index, dindex, rindex = loadData()
print len(mat), max_index, len(dindex), len(rindex)


M = N = max_index
K = 50
print "The actual matrix size is %d-by-%d." %(N, M)

row = np.array([ x[0] for x in mat.keys() ])
col = np.array([ x[1] for x in mat.keys() ])
data = np.array(mat.values())
mat  = coo_matrix((data, (row, col)), shape=(M, N)).toarray()
mask = coo_matrix((np.array([1]*len(row)), (row, col)), shape=(M, N)).toarray()
print mat.shape, mask.shape

if loadFromDisk:
    U = np.load('nU_250.npy')
    V = np.load('nV_250.npy')
    B = np.load('nB_250.npy')
    C = np.load('nC_250.npy')
else:
    U = np.random.rand(M,K)
    V = np.random.rand(K,N)
    B = np.zeros(M)
    C = np.zeros(N)

nU, nV, nB, nC = matrix_factorization(U, V, B, C)
print "matrix factorization is done."

np.save('nU_'+str(t), U)
np.save('nV_'+str(t), V)
np.save('nB_'+str(t), B)
np.save('nC_'+str(t), C)

