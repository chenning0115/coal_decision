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

    def search(self,query,target_case_monitor=None):
        id_grad_list, query_list = self.search_algorithm_new(query)
        case_obj_list = []
        for _id, grad in id_grad_list:
            # print(_id,grad)
            temp_obj = CaseObj(_id)
            temp_obj.query = query
            temp_obj.query_list = query_list
            temp_obj.match_grad = grad
            temp_obj.target_case_fixed = target_case_fixed
            temp_obj.sim_result = calculate_sim(temp_obj.res, target_case_fixed, target_case_monitor)
            temp_obj.cal_grad()
            case_obj_list.append(temp_obj)
        case_obj_list = sorted(case_obj_list, key= lambda x: x.grad, reverse=True)
        return case_obj_list


    def search_algorithm_new(self, query):
        # words = self.seg.segment_for_search(query)
        words = self.seg.segment_for_query(query)
        idset = set()
        word_id2num = {}
        for word,stop in words:
            id2num = self.indexer.find(word)
            word_id2num[word] = id2num
            idset.update(set(id2num.keys()))
        ids = list(idset)
        id2index = {_id:i for i,_id in enumerate(ids)}
        title_matrix = [[0]*len(words) for i in range(len(ids))]
        content_matrix = [[0]*len(words) for i in range(len(ids))]
        for wi, (word,stop) in enumerate(words):
            id2num = word_id2num[word]
            for _id, item in id2num.items():
                _id_index = id2index[_id]
                title_matrix[_id_index][wi] = item['TITLE']
                content_matrix[_id_index][wi] = item['CONTENT']
        title_matrix = np.asarray(title_matrix)
        content_matrix = np.asarray(content_matrix)
        def mystd(data):
            mean = np.mean(data,axis=0)
            std = np.std(data,axis=0)+1e-5
            return (data-mean)/std
        # print([word for word,s in words])
        # print(content_matrix)
        title_matrix = mystd(title_matrix)
        content_matrix = mystd(content_matrix)
        fuse_matrix = 0.6 * title_matrix + 0.4 * content_matrix
        
        def querywords_weight(words): 
            res = []
            for word,stop in words:
                if stop:
                    res.append(0) #停止词权重为0
                else:
                    res.append(2**(len(word)-1)) #长度越大，权重越高
            return np.asarray(res)
        
        weight = querywords_weight(words)
        grad = np.sum(fuse_matrix*weight, 1)
        # print(grad)
        def linear_map(l, a=0, b=10):
            x,y = np.min(grad),np.max(grad)
            if y-x==0:
                return np.asarray(list(range(len(grad))))
            return (grad-x)/(y-x) * (b-a) + a
        grad = linear_map(grad)
        res = [[_id,i] for _id,i in zip(ids,list(grad))]
        final_words = [word for word,s in words]
        return res, final_words
            



    def search_algorithm(self,query):
        ratio_title = 0.7
        ratio_content = 0.3
        def querywords_weight(words): 
            res = []
            for word,stop in words:
                if stop:
                    res.append([word,0]) #停止词权重为0
                else:
                    res.append([word, 2**(len(word)-1)]) #长度越大，权重越高
            return res
        
        words = self.seg.segment_for_query(query)
        words = querywords_weight(words)
        id2grad = defaultdict(int)
        for word, w in words:
            id2num = self.indexer.find(word)
            # print(word, id2num)
            for _id, item in id2num.items():
                id2grad[_id] += item['TITLE'] * ratio_title + min(item['CONTENT'],100) * ratio_content
        id_grad = [[_id,grad] for _id,grad in id2grad.items()]
        
        #需要将所有的数字映射到[0-10]
        def math_match(id_grad,a=0,b=10):
            id_grad = sorted(id_grad, key=lambda x: x[1],reverse=True)
            x,y = id_grad[0][1],id_grad[-1][1]
            inter = float(x - y)
            for ig in id_grad:
                if inter == 0:
                    ig[1] = a
                else:
                    ig[1]= (ig[1] - y)/inter * (b-a) + a
            print('match_grad=',ig[1])
            return id_grad
        id_grad = math_match(id_grad,0,10)
        final_words = [word for word,s in words]
        return id_grad, final_words

    

if __name__ == "__main__":
    ss = Search()
    ss.search_algorithm_new('瓦斯超限')
    # ss.search('瓦斯爆炸')

