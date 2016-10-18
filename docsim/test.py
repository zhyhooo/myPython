from segmenter import Segmenter


seg = Segmenter()
tokens = seg.cut_line("hello world")
print '|'.join(tokens)
