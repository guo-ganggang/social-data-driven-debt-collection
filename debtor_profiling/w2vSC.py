#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os.path
import sys
import multiprocessing

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

if __name__ == '__main__':
    program = os.path.basename(sys.argv[0])
    logger = logging.getLogger(program)

    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.INFO)
    logger.info("running %s" % ' '.join(sys.argv))

    # check and process input arguments

    inp = 'D:\\pingan_stock\\pingan_stock_undervalueed\\0407\\zhongxin\\zhongxin_bbs_seg_clean_3words.csv'
    outp1 = 'D:\\pingan_stock\\pingan_stock_undervalueed\\0407\\word2vec_zhongxin_bbs\\sg0_s200_w3_m2_3words.bin'
    outp2 = 'D:\\pingan_stock\\pingan_stock_undervalueed\\0407\\word2vec_zhongxin_bbs\\sg0_s200_w3_m2_3words.vector'

    # model = Word2Vec(LineSentence(inp), size=200,window=5,min_count=100,
    #         workers=multiprocessing.cpu_count(), hs=1, negative=0)

    model = Word2Vec(LineSentence(inp),sg = 0, size=200,window=3,min_count=2,
            workers=multiprocessing.cpu_count(), hs=1, negative=3,sample = 1e-4)

    # trim unneeded model memory = use(much) less RAM
    #model.init_sims(replace=True)
    model.save_word2vec_format(outp2, binary=False)
    model.save(outp1)