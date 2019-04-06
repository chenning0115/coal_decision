import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
import math
from mongo import find_one,meta_MKJB,meta_KJWSDJ


class CaseObj(object):
    def __init__(self,_id):
        self._id = _id 
        self.res = find_one(_id)
        self.sid = self.res['SGALBH']
        self.query = None
        self.query_list = None
        self.match_grad = None

        self.target_case_fixed = None
        self.sim_result = None
        self.sim_grad = None 

        self.grad = 0

        self.mathch_ratio = 0.5
        self.sim_ratio = 0.5

        self.url_prefix = "find_one"

    def cal_grad(self):
        if self.match_grad:
            self.grad += (self.mathch_ratio * self.match_grad)
        if self.sim_grad:
            self.grad += (self.sim_ratio * self.sim_grad)
        # print('sim=%s,raw_sim=%s, match=%s' % (self.sim_grad, self.sim_result.cal_sim_grad(),self.match_grad))
        return self.grad

    def get_grads(self):
        match_grad = self.match_grad if self.match_grad else 0
        sim_grad = self.sim_grad if self.sim_grad else 0
        text = "搜索指数:%s,匹配指数%s,综合指数:%s" % tuple(["<hltext>%.2f</hltext>" %  s for s in [match_grad,sim_grad,self.grad]])
        # print(text)
        return text

    def get_labels(self):
        labels = []
        if not self.sim_result:
            return labels
        for item in self.sim_result.sim_item_list:
            if item.raw_grad > 0:
                labels.append("<span class='text-%s'>%s</span>" % (item.color, item.info))
        return ",".join(labels)

    def get_url_ori(self):
        return "%s?_id=%s&_query=%s" % (self.url_prefix, self._id, self.query)

    def get_title_search(self):
        title = ""
        title_raw = self.res['TITLE']
        for char in title_raw:
            if char in self.query:
                char = '<hltext> ' + char + ' </hltext>'
            title += char
        return title

    def get_content_search(self):
        res = []
        temp_list = [(q,len(q)) for q in self.query_list]
        temp_list = sorted(temp_list,key=lambda  x: x[1])
        temp_list = [q[0] for q in temp_list]
        for query in temp_list:
            res.append(self.get_content_search_one(query))
        return ".........".join(res[0:5])

    def get_content_search_one(self, cur_query):
        string = self.res['CONTENT']
        if len(cur_query)>0:
            cur = string.find(cur_query)
        else:
            cur = 0
        i = max(0, cur - 20)
        j = cur + 40
        origin = string[i:j]
        returnString = ''
        for char in origin:
            if char in self.query:
                char = '<hltext>' + char + '</hltext>'
            returnString += char
        return returnString

    def get_title(self):
        return  str(self.res['XSGJBXX']['SGDD']) \
              + str(self.res['XSGJBXX']['SGLX']) + "事故"
    

    def format_mydoc(self):
        self.mydoc = {}
        self.mydoc.update(self.res)
        
        def high_light(content):
            if self.query:
                returnString = ''
                for char in content:
                    if char in self.query:
                        char = '<hltext>' + char + '</hltext>'
                    returnString += char
            else:
                returnString = content
            return returnString

        self.mydoc['XSGGC'] = high_light('\n'.join(["<p>"+str(l).strip()+"</p>" for l in str(self.mydoc['XSGGC']).split()]))
        self.mydoc['XSGFFCS'] = high_light('\n'.join(["<p>"+str(l).strip()+"</p>" for l in str(self.mydoc['XSGFFCS']).split()]))
        self.mydoc['XSGJYCS'] = high_light('\n'.join(["<p>"+str(l).strip()+"</p>" for l in str(self.mydoc['XSGJYCS']).split()]))
        self.mydoc['XSGDZSWTJ']['DZGZFZCD'] = high_light(str(self.mydoc['XSGDZSWTJ']['DZGZFZCD']))
        self.mydoc['XSGDZSWTJ']['SGSWDZHJ'] = high_light(str(self.mydoc['XSGDZSWTJ']['SGSWDZHJ']))
        for i in ['ZJYY','JJYY','RWYY','JXYY','GLYY','HJYY']:
            self.mydoc['XSGYY'][i] = high_light('\n'.join(["<p>"+str(l).strip()+"</p>" for l in str(self.mydoc['XSGYY'][i]).split()]))
        # print(self.mydoc)
        
        if  not math.isnan(float(self.mydoc['XKJXX']['MKJB'])):
            self.mydoc['XKJXX']['MKJB'] = meta_MKJB[int(self.mydoc['XKJXX']['MKJB'])]
        if not math.isnan(float(self.mydoc['XKJXX']['KJWSDJ'])):
            self.mydoc['XKJXX']['KJWSDJ'] = meta_KJWSDJ[int(self.mydoc['XKJXX']['KJWSDJ'])]

        return self.mydoc


    # def get(self, first, second=None):
    #     temp = self.res[first]
    #     if second:
    #         return temp[second]
    #     else:
    #         return first

    # def gett(self, first, second=None):
    #     temp = self.res[first]
    #     if second:
    #         return '\n'.join(["<p>"+l.strip()+"</p>" for l in temp[second].split()])
    #     else:
    #         return '\n'.join(["<p>"+l.strip()+"</p>" for l in temp.split()])




def find_one_obj(_id=""):
    return CaseObj(_id)