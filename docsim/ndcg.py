# reference: https://en.wikipedia.org/wiki/Discounted_cumulative_gain
import sys
import math


def nDCG( scores ):
    '''
    calculate nDCG@k
    '''
    DCGk = 0
    for i, score in enumerate(scores):
        DCGk += (( 2**score - 1 ) / math.log( i+2, 2 ))
    IDCGk = sum( [ (2**x-1)/math.log(i+2, 2) for i, x in enumerate(sorted(scores, reverse=True)) ] )

    return DCGk/IDCGk




if __name__=="__main__":
    
    finput = sys.argv[1]
    k = int(sys.argv[2])
    '''
      finput is in the format of:
          query \t sku \t score \t pos
      here k is the value of p in wiki page
    '''

    fin = open(finput, 'r')
    out = []
    last_query, scores = '', []
    for line in fin:
        try:
            if len(line.strip().split('\t'))==5:
                query, sku, score, pos, cos = line.strip().split('\t')
            else:
                query, sku, score, pos = line.strip().split('\t')
        except:
            print line.strip()
        if query == last_query:
            scores.append(int(score))
        else:
            scores = scores[:k]
            #if len(set(scores)) <= 1:
            if not any(scores):
                last_query, scores = query, [ int(score) ]
                continue
            out.append( (last_query, nDCG(scores) ) )
            last_query, scores = query, [ int(score) ]
    if query == last_query:
        scores = scores[:k]
        out.append( (last_query, nDCG(scores)) )

    
    for tuple in out:
        print "nDCG of {} is {}".format( tuple[0], tuple[1] )
    if out:
        print "Average is {}".format( sum([ x[1] for x in out])/len(out) )
