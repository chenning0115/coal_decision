import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
from reverse_index import Segmenter,Indexer
from collections import defaultdict
from caseobj import CaseObj
from simcase import target_case_fixed,calculate_sim

class Search(object):
    def __init__(self):
        self.seg = Segmenter()
        self.indexer = Indexer()

    def search(self,query):
        id_grad_list = self.search_algorithm(query)
        case_obj_list = []
        for _id, grad in id_grad_list:
            temp_obj = CaseObj(_id)
            temp_obj.query = query
            temp_obj.match_grad = grad
            temp_obj.target_case_fixed = target_case_fixed
            temp_obj.sim_result = calculate_sim(temp_obj.res, target_case_fixed)
            temp_obj.cal_grad()
            case_obj_list.append(temp_obj)
        case_obj_list = sorted(case_obj_list, key= lambda x: x.grad, reverse=True)
        return case_obj_list

    def search_algorithm(self,query):
        ratio_title = 0.7
        ratio_content = 0.3
        def querywords_weight(words): 
            res = []
            for word,stop in words:
                if stop:
                    res.append([word,0]) #停止词权重为0
                else:
                    res.append([word, 2**len(word)]) #长度越大，权重越高
            return res
        
        words = self.seg.segment_for_query(query)
        words = querywords_weight(words)
        id2grad = defaultdict(int)
        for word, w in words:
            id2num = self.indexer.find(word)
            for _id, item in id2num.items():
                id2grad[_id] += item['TITLE'] * ratio_title + min(item['CONTENT'],5) * ratio_content
        id_grad = [[_id,grad] for _id,grad in id2grad.items()]
        id_grad = sorted(id_grad, key=lambda x: x[1],reverse=True)
        return id_grad

    

if __name__ == "__main__":
    ss = Search()
    ss.search('瓦斯爆炸')

