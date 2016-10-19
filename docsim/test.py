# -*- coding: utf-8 -*-
from segmenter import Segmenter


seg = Segmenter()
tokens = seg.cut_line("本文为博主原创文章，未经博主允许不得转载。")
print tokens
#print '|'.join(tokens)
