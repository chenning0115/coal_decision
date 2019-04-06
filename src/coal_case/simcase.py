import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
from mongo import meta_MKJB,meta_KJWSDJ

target_case_fixed = {
    "GZMLX":("回采工作面",4), #地点信息 9
    "KJWSDJ":("3",4), #矿井瓦斯等级 1   
    "MCHD":("5.4",4), #煤层厚度 3
    "PJQJ":("6",4), #平均倾角 2
    "MCZRQX":("无自燃倾向",4), # 煤层自燃倾向 4

    "SJSCNL2":("438",3),#年产量 5
    "KJTFFS":("混合式通风",3), #矿井通风方式 6
    "JFXXS":("0.21",3), #坚固性系数 7
    "TQXXS":("0.175",3),#透气性系数 8

    "ZXCD":("1257",2), #走向长度 10
    "GZMCD":("220",2), #工作面长度 11

    "MCBZ":("无爆炸倾向",1), # 煤尘爆炸倾向 12
    "MKJB":("3",1), #煤矿级 别 国有煤矿等 14
    "KJKCFS":("综合开拓",1), #矿井开采方式 13


    # "ZQJDWSYCL":("83",0), #绝对瓦斯涌出量
    # "MKLX":("地下煤矿",0),
    # "DZGZFZCD":("地质构造复杂程度中等",0),
    # "SGSWDZHJ":("本井田基本属水文地质条件简单型",0),
    # "RCL":("1.2",0), #日产量
}

#该处需要由调用方主动提供
target_case_monitor = {
    "CH4HL":("",0),
    "CO2HL":("",0),
    "COHL":("",0),
    "QTJCHS":("",0)
}


class SimItem(object):
    def __init__(self,_doc, _tar,_r):
        self.src_doc = _doc
        self.src = None
        self.tar = _tar
        self.r = _r
        self.raw_grad = 0
        self.info = None
        self.color = "success"
    def cal_grad(self):
        self.grad = self.raw_grad *  self.r
        return self.grad
    def __str__(self):
        return 'SimItem:src=%s,tar=%s,r=%s,raw_grad=%s,grad=%s,info=%s' % (self.src, self.tar, self.r, self.raw_grad,self.grad,self.info)

    

class SimResult(object):
    def __init__(self, sim_item_list):
        self.sim_item_list = sim_item_list
    
    def sort(self):
        self.sim_item_list.sort(key=lambda item: item.grad, reverse=True)

    def cal_sim_grad(self):
        sum_grad = 0
        for item in self.sim_item_list:
            sum_grad += item.grad
        self.grad = sum_grad
        return self.grad


def SimRank(sim_item, col, new_col,label):
    try:
        sim_item.src = sim_item.src_doc[col]
        sim_item.raw_grad = int(sim_item.src_doc[new_col])
        sim_item.info = ""
    except:
        sim_item.raw_grad = 0
        sim_item.info = ""
    return sim_item



def SimSJSCNL2(sim_item):
    return SimRank(sim_item, 'SJSCNL2', 'RANK_SJSCNL2','年产量')

def SimZXCD(sim_item):
    return SimRank(sim_item, 'ZXCD', 'RANK_ZXCD','走向长度')

def SimGZMCD(sim_item):
    return SimRank(sim_item, 'GZMCD', 'RANK_GZMCD','工作面长度')

def SimJFXXS(sim_item):
    return SimRank(sim_item, 'JFXXS', 'RANK_JFXXS','坚固性系数')

def SimTQXXS(sim_item):
    return SimRank(sim_item, 'TQXXS', 'RANK_TQXXS','透气性系数')


def SimGZMLX(sim_item):#工作面类型
    try:
        sim_item.src = sim_item.src_doc['GZMLX']
        src, tar = sim_item.src.strip(), sim_item.tar.strip()
        if src == tar:
            sim_item.raw_grad = 10
            sim_item.info = "同为%s事故" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "事故位置不同" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知位置"
    return sim_item


def SimMCHD(sim_item): #煤尘爆炸倾向
    def get_class(n):
        n = float(n)
        if n < 1.3:
            return (0,"薄煤层")
        elif n < 3.5:
            return (1,"中厚煤层")
        elif n < 8.0:
            return (2,"厚煤层")
        else:
            return (3,"巨厚煤层")
    sim_item.src = sim_item.src_doc['MCHD']
    src, tar = sim_item.src, sim_item.tar
    src, tar = float(src), float(tar)
    src_rank, src_label = get_class(src)
    tar_rank, tar_label = get_class(tar)
    t = abs(src_rank - tar_rank)
    if t == 0:
        sim_item.raw_grad = 10
        sim_item.info = "同为%s" % src_label
    elif t == 1:
        sim_item.raw_grad = 3
        sim_item.info = "煤层厚度相近"
    elif t == 2:
        sim_item.raw_grad = 0
        sim_item.info = "不同煤层厚度"
    elif t == 3:
        sim_item.raw_grad = 0
        sim_item.info = "煤层厚度差异较大"

def SimMCZRQX(sim_item):#煤层自燃倾向
    try:
        sim_item.src = sim_item.src_doc['MCZRQX']
        src, tar = sim_item.src.strip(), sim_item.tar.strip()
        if src == tar:
            sim_item.raw_grad = 10
            sim_item.info = "煤层同%s" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同煤层自燃倾向" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知煤层自燃倾向"
    return sim_item

def SimMCBZ(sim_item):#煤层爆炸倾向
    try:
        sim_item.src = sim_item.src_doc['MCBZ']
        src, tar = sim_item.src.strip(), sim_item.tar.strip()
        if src == tar:
            sim_item.raw_grad = 10
            sim_item.info = "煤尘同%s" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同煤尘爆炸倾向" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知煤尘爆炸倾向"
    return sim_item


def SimPJQJ(sim_item):#煤层倾角
    def get_class(n):
        n = float(n)
        if n < 8:
            return (0,"近水平煤层")
        elif n < 25:
            return (1,"缓倾斜煤层")
        elif n < 45:
            return (2,"倾斜煤层")
        else:
            return (3,"急倾斜煤层")
    sim_item.src = sim_item.src_doc['PJQJ']
    src, tar = sim_item.src, sim_item.tar
    src, tar = float(src), float(tar)
    src_rank, src_label = get_class(src)
    tar_rank, tar_label = get_class(tar)
    t = abs(src_rank - tar_rank)
    if t == 0:
        sim_item.raw_grad = 10
        sim_item.info = "同为%s" % src_label
    elif t == 1:
        sim_item.raw_grad = 3
        sim_item.info = "煤层倾角相近"
    elif t == 2:
        sim_item.raw_grad = 0
        sim_item.info = "不同煤层倾角"
    elif t == 3:
        sim_item.raw_grad = 0
        sim_item.info = "煤层倾角差异较大"


def SimMKJB(sim_item): #煤矿级别
    try:
        sim_item.src = sim_item.src_doc['XKJXX']['MKJB']
        src, tar = sim_item.src, sim_item.tar
        src, tar = int(src), int(tar)
        if abs(src-tar)==0:
            sim_item.raw_grad = 10
            sim_item.info = "同为%s" % meta_MKJB[tar]
        elif abs(src-tar)==1:
            sim_item.raw_grad = 0
            sim_item.info = "不同级别煤矿"
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同煤矿级别" 
    except:
            sim_item.raw_grad = 0
            sim_item.info = "未知煤矿级别" 
    return sim_item

def SimMKLX(sim_item):
    try:
        sim_item.src = sim_item.src_doc['XKJXX']['MKLX']
        src, tar = sim_item.src.strip(), sim_item.tar.strip()
        if src == tar:
            sim_item.raw_grad = 10
            sim_item.info = "同为%s" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同煤矿类型" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知煤矿类型"
    return sim_item

def  SimKJWSDJ(sim_item): #瓦斯等级
    try:
        sim_item.src = sim_item.src_doc['XKJXX']['KJWSDJ']
        src, tar = sim_item.src, sim_item.tar
        src, tar = int(src), int(tar)
        if abs(src-tar)==0:
            sim_item.raw_grad = 10
            sim_item.info = "同为%s" % meta_KJWSDJ[tar]
        elif abs(src-tar)==1:
            sim_item.raw_grad = 5
            sim_item.info = "相似瓦斯等级"
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同瓦斯等级" 
    except:
            sim_item.raw_grad = 0
            sim_item.info = "未知瓦斯等级" 
    return sim_item

def SimKJKCFS(sim_item):
    try:
        sim_item.src = sim_item.src_doc['XKJXX']['KJKCFS']
        src, tar = sim_item.src.strip(), sim_item.tar.strip()
        if src == tar:
            sim_item.raw_grad = 10
            sim_item.info = "同为%s" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同开采方式" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知开采方式"
    return sim_item

def SimKJTFFS(sim_item):
    try:
        sim_item.src = sim_item.src_doc['XKJXX']['KJTFFS']
        src, tar = sim_item.src.strip(), sim_item.tar.strip()
        if src == tar:
            sim_item.raw_grad = 10
            sim_item.info = "同为%s" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同通风方式" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知通风方式"
    return sim_item

def calculate_sim(doc, target_case_fixed, target_case_monitor=None):
    fixed_use_list = ['MKJB','KJWSDJ','KJKCFS','KJTFFS','GZMLX',\
                        'MCHD','PJQJ','MCZRQX','MCBZ','SJSCNL2','ZXCD','GZMCD','TQXXS','JFXXS']
    sim_item_list = []
    for t in fixed_use_list:
        tar_val, r = target_case_fixed[t]
        sim_item = SimItem(doc,tar_val,r)
        eval("Sim%s(sim_item)" % t)
        sim_item.cal_grad()
        print('%s %s,%s grad=%s,%s'  % (sim_item.info,sim_item.src, sim_item.tar, sim_item.raw_grad, sim_item.grad))
        sim_item_list.append(sim_item)
    sim_res = SimResult(sim_item_list)
    sim_res.sort()
    sim_res.cal_sim_grad()
    # print("final_grad=",sim_res.grad)
    # print('-------------------')
    return sim_res


    

if __name__ == "__main__":
    from mongo import find_one
    doc = find_one("5ca57c7e230b947dfa7aa377")
    sim_res = calculate_sim(doc, target_case_fixed, target_case_monitor)
    print(sim_res.grad)
    for si in sim_res.sim_item_list:
        print(si)
    


