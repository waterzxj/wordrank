#/usr/bin/env python
#coding:utf-8


import jieba
from collections import OrderedDict
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class WordRank(object):
    """
    the demo of wordrank algorithm
    """
    def __init__(self, idf_path = None):
        if idf_path:
            self.idf_path = idf_path
        else:
            self.idf_path = "./idf.txt"

        self.init = False    
        self.idf_dict = {}

    def t_init(self):
        if self.init == False:
            self.load_dict()

        self.final_term_dict = OrderedDict()   
        self.init_term_dict = OrderedDict()
        self.init = True

    def load_dict(self):
        with open(self.idf_path) as fin:
            for line in fin:
                parts = line.rstrip("\n").split(" ")
                term = parts[0]
                weight = parts[1]
                self.idf_dict[term] = float(weight)
        
        self.init = True

    def query_analysis(self, query):
        #step1 segword
        self.seg_list = jieba.cut(query, cut_all = False)
        #step2 idf init term weight and deduplicate term
        for term in self.seg_list:
            term = term.encode('utf-8')
            if term in self.idf_dict:
                term_weight = self.idf_dict[term]
            else:
                term_weight = 0.0

            self.init_term_dict[term] = term_weight
            self.final_term_dict[term] = term_weight

        #step3 chunk weight
        self.chunk_analysis(self.init_term_dict.keys())

    def rerank_term_weight(self, terms, index_i, index_j, rerank_weight):
        term_i = terms[index_i]
        term_j = terms[index_j]

        init_weight_i = self.init_term_dict[term_i]
        init_weight_j = self.init_term_dict[term_j]

        self.final_term_dict[term_i] = self.final_term_dict[term_i] + rerank_weight *  \
                                (float(init_weight_i) / ((init_weight_i + init_weight_j)))

        self.final_term_dict[term_j] = self.final_term_dict[term_j] + rerank_weight *  \
                                (init_weight_j / ((init_weight_i + init_weight_j)))

    def combinations(self, index, terms):
        if index >= len(terms):
            return

        for i in range(index+1, len(terms)):
            tmp = terms[index] + terms[i]
            if tmp in self.idf_dict:
                rerank_weight = self.idf_dict[tmp]
                self.rerank_term_weight(terms, index, i, rerank_weight)

        return         

    def chunk_analysis(self, terms):
        for i in range(len(terms)):
            self.combinations(i, terms)

    def normalize(self):
        final_res = OrderedDict()
        sum_weight = sum([value for value in self.final_term_dict.values()])

        for k,v in self.final_term_dict.iteritems():
            final_res[k] = v / float(sum_weight)

        return final_res    

    def wordrank(self, query):
        if self.init == False:
            self.t_init()

        self.query_analysis(query)    
        final_res = self.normalize()

        #方便ipython看结果
        print "\t".join([item[0] + ":" + str(item[1]) for item in tuple(final_res.iteritems())])
        return tuple(final_res.iteritems())



if __name__ == "__main__":
    wordrank = WordRank()
    wordrank.wordrank("百度世界大会")
    


