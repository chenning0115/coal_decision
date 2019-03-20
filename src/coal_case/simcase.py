import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
from mongo import meta_MKJB,meta_KJWSDJ

target_case_fixed = {
    "QYMC":("阳煤集团寺家庄煤矿",1),
    "QYXZ":("有限责任公司",1),
    "MKJB":("3",1),
    "MKLX":("地下煤矿",1),
    "WZYZ":("是",1),
    "SPTG":("是",1),
    "SJSCNL1":("500",1),
    "SJSCNL2":("500",1),
    "CYRYSL":("",1),
    "KJWSDJ":("3",1),
    "KJKCFS":("综合开拓",1),
    "KJTFFS":("混合式通风",1),
    "DZGZFZCD":("地质构造复杂程度中等",1),
    "SGSWDZHJ":("本井田基本属水文地质条件简单型",1)
}

#该处需要由调用方主动提供
target_case_monitor = {
    "CH4HL":("",1),
    "CO2HL":("",1),
    "COHL":("",1),
    "QTJCHS":("",1)
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


def SimMKJB(sim_item): #煤矿级别
    try:
        sim_item.src = sim_item.src_doc['XKJXX']['MKJB']
        src, tar = sim_item.src, sim_item.tar
        src, tar = int(src), int(tar)
        if abs(src-tar)==0:
            sim_item.raw_grad = 1
            sim_item.info = "同为%s" % meta_MKJB[tar]
        elif abs(src-tar)==1:
            sim_item.raw_grad = 0.5
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
            sim_item.raw_grad = 1
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
            sim_item.raw_grad = 1
            sim_item.info = "同为%s" % meta_KJWSDJ[tar]
        elif abs(src-tar)==1:
            sim_item.raw_grad = 0.5
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
            sim_item.raw_grad = 1
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
            sim_item.raw_grad = 1
            sim_item.info = "同为%s" % tar
        else:
            sim_item.raw_grad = 0
            sim_item.info = "不同通风方式" 
    except:
        sim_item.raw_grad = 0
        sim_item.info = "未知通风方式"
    return sim_item

def calculate_sim(doc, target_case_fixed, target_case_monitor=None):
    fixed_use_list = ['MKJB','MKLX','KJWSDJ','KJKCFS','KJTFFS']
    sim_item_list = []
    for t in fixed_use_list:
        tar_val, r = target_case_fixed[t]
        sim_item = SimItem(doc,tar_val,r)
        eval("Sim%s(sim_item)" % t)
        sim_item.cal_grad()
        sim_item_list.append(sim_item)
    sim_res = SimResult(sim_item_list)
    sim_res.sort()
    sim_res.cal_sim_grad()
    return sim_res


    

if __name__ == "__main__":
    from mongo import find_one
    doc = find_one("5c8fa0fb230b945f6e4de092")
    sim_res = calculate_sim(doc, target_case_fixed, target_case_monitor)
    print(sim_res.grad)
    for si in sim_res.sim_item_list:
        print(si)
    


