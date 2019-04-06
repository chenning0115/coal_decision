import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pymongo import MongoClient
from bson.objectid import ObjectId
from collections import defaultdict,Counter
import numpy as np
import pandas as pd
import json
import jieba
from mongo import get_mongo_conn2coaldb, mongo_collection_rawdata


path_vocab = os.path.join(os.path.dirname(__file__),"../../data/vocab/vocab_0.txt") 
path_stop = os.path.join(os.path.dirname(__file__),"../../data/vocab/stopwords_0.txt")
path_index = os.path.join(os.path.dirname(__file__),"../../data/vocab/index_new.txt")


class Segmenter(object):
    def __init__(self,_path_vocab = path_vocab,_path_stopwords = path_stop):
        self.path_vocab = _path_vocab
        self.path_stopwords = _path_stopwords

        if  self.path_vocab:
            jieba.load_userdict(self.path_vocab)
        self.set_stopwords = set()
        if self.path_stopwords:
            with open(self.path_stopwords,'r') as fin:
                print('start to load stop words!')
                line = fin.readline()
                while(line!=''):
                    self.set_stopwords.add(line.strip())
                    line = fin.readline()
            print('load stop words successfully!')
    # segment the given context for search engien. stopwords will be removed if True
    def segment_for_search(self,context,stopwords=False):
        seg_gen = jieba.cut_for_search(context)
        res = []
        if stopwords:
            for w in seg_gen:
                if w not in self.set_stopwords:
                    res.append(w)
        else:
            res = list(seg_gen)
        return res
    
    # which method is the best query segmentation method?
    def segment_for_query(self,context):
        # seg_gen = jieba.cut(context)
        seg_gen = jieba.cut_for_search(context)
        res = []
        for w in seg_gen:
            if w in self.set_stopwords:
                res.append((w,True))
            else:
                res.append((w,False))
        return res
        
    def seg_doc(self, item):
        word2num = defaultdict(dict)
        _id, title, content = item["_id"], item["TITLE"],item["CONTENT"]
        seg_title = self.segment_for_search(title)
        title_kv = Counter()
        for word in seg_title:
            title_kv[word] += 1
        seg_content = self.segment_for_search(content)
        content_kv = Counter()
        for word in seg_content:
            content_kv[word] += 1
        words = set()
        words.update(set(title_kv.keys()))
        words.update(set(content_kv.keys()))
        for word in words:
            word2num[word] = {
                "TITLE": title_kv[word] if word in title_kv else 0,
                "CONTENT": content_kv[word] if word in content_kv else 0
            }
        return str(_id), word2num


    def seg_all(self, path_save=path_index):
        #只segment TITLE 和 CONTENT
        word2id = defaultdict(dict)
        db_mongo = get_mongo_conn2coaldb()
        rawdata_gen = db_mongo[mongo_collection_rawdata].find()
        for index, item in enumerate(rawdata_gen):
            _id, word2num = self.seg_doc(item)
            for word in word2num.keys():
                word2id[word][_id] = word2num[word]
            if index % 10 == 0:
                print('index done of %s' % index)

        with open(path_save,'w') as fout:
            fout.write(json.dumps(word2id))
            print('done!')
            
            
class Indexer(object):
    def __init__(self, path_index=path_index):
        self.path_index = path_index
        self.word2id = None
        with open(path_index, 'r') as fin:
            self.word2id = json.loads(fin.read())
        
    def find(self, word):
        if word in self.word2id:
            return self.word2id[word]
        else:
            return {}



if __name__ == "__main__":
    seg = Segmenter(path_vocab, path_stop)
    seg.seg_all(path_index)

