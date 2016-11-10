feature=[
'IsSource','IsClick','IsOrder','IsFocus','IsZeus','IsHotsale','IsOffline','IsOrdRelate','IsCompany','IsSearch','IsFunny', 'IsOthers',

schema = ['expid','pin', 'req_tm', 'sid', 'pos', 'sku', 'matchType','click_ts','ord_ts','action']
schema.extend(featureplus)
if __name__=='__main__':
    print "schema: %d" %len(schema)
    print "feature: %d" %len(feature)
    #print schema    
