import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import pandas as pd

#mongodb info
mongo_url = "mongodb://localhost:27017"
mongo_db_name = "coal_decision"
mongo_collection_rawdata = "coal_accident_case_new"

# mongo object already threadpool, so just create the mongo instance instead of using singleton schema
def get_mongo_conn2coaldb():
    return MongoClient(mongo_url)[mongo_db_name]

def insert2mongo(collect, _id, doc):
    try:
        doc['_id'] = ObjectId(_id)
        collect.insert(doc)
    except Exception as e:
        print('insert %s failed, for %s' %(_id, str(e)))
        return False
    return True
        
    
case_meta = {
    "XQYXX":"企业信息",
    "XKJXX":"矿井信息",
    "XSGJBXX":"事故基本信息",
    "XSGDZSWTJ":"事故地质水文条件",
    "XSGJCXX":"事故监测信息",
    "XSGGC":"事故过程",
    "XSGYY":"事故原因",
    "XSGJYCS":"事故救援措施",
    "XSGSSXX":"事故损失信息",
    "XSGFFCS":"事故防范措施",

    'SGALBH': '事故案例编号',
    'SGGCMSYW': '事故过程描述原文',
    'SGYYFXYW': '事故原因分析原文',
    'SGJYCSYW': '事故救援措施原文',
    'SGFFCSYW': '事故防范措施原文',
    'BZ1': '备注1',
    'SGALBH.1': '事故案例编号',
    'QYMC': '企业名称',
    'QYXZ': '企业性质',
    'MKJB': '煤矿级别',
    'MKLX': '煤矿类型',
    'WZYZ': '五证一照齐全情况',
    'SPTG': '审批通过',
    'SJSCNL1': '设计生产能力（万吨/年）',
    'SJSCNL2': '实际生产能力（万吨/年）',
    'CYRYSL': '从业人员数量',
    'ZQXDWSYCL': '灾前相对瓦斯涌出量（m3/t）',
    'ZQJDWSYCL': '灾前绝对瓦斯涌出量（m3/min）',
    'ZHWSYCL': '灾后瓦斯涌出量（m3）',
    'KJWSDJ': '矿井瓦斯等级',
    'KJKCFS': '矿井开采方式',
    'KJTFFS': '矿井通风方式',
    'BZ2': '备注2',
    'SGALBH.2': '事故案例编号',
    'SGSJ': '事故时间',
    'SGDD': '事故地点',
    'SGLX': '事故类型',
    'SGXZ': '事故性质',
    'DZGZFZCD': '地质构造复杂程度',
    'SGSWDZHJ': '事故水文地质环境',
    'BZ3': '备注3',
    'SGALBH.3': '事故案例编号',
    'SWRS': '死亡人数',
    'SWRS.1': '死亡人数',
    'SSRS': '受伤人数',
    'SSRS.1': '受伤人数',
    'ZJJJSS': '直接经济损失（万元）',
    'ZJJJSS.1': '直接经济损失（万元）',
    'JJJJSS': '间接经济损失（万元）',
    'YJXYJB': '应急响应级别',
    'YXFW': '影响范围',
    'CH4HL': 'CH4含量（%）',
    'CO2HL': 'CO2含量（%）',
    'COHL': 'CO含量（%）',
    'QTJCHS': '其他监测参数',
    'BZ4': '备注4',
    'SGALBH.4': '事故案例编号',
    'ZJYY': '直接原因',
    'JJYY': '间接原因',
    'RWYY': '人为原因',
    'JXYY': '机械原因',
    'GLYY': '管理原因',
    'HJYY': '环境原因',
    'BZ5': '备注5',
    'SGALBH.5': '事故案例编号',
    'DDPZZY1': '调度配置资源1',
    'DDPZZY2': '调度配置资源2',
    'DDPZZY3': '调度配置资源3',
    'DDPZZY4': '调度配置资源4',
    'DDPZZY5': '调度配置资源5',
    'BZ6': '备注6',
    'SGALBH.6': '事故案例编号',
    'ZZH': '总指挥',
    'FZZH': '副总指挥',
    'YJJYZJ1': '应急救援专家1',
    'YJJYZJ2': '应急救援专家2',
    'YJJYZJ3': '应急救援专家3',
    'YJJYCY1': '应急救援成员1',
    'YJJYCY1.1': '应急救援成员2',
    'YJJYCY1.2': '应急救援成员3',
    'YJJYCY1.3': '应急救援成员4',
    'YJJYCY1.4': '应急救援成员5',
    'BZ7': '备注7',
    'SGALBH.7': '事故案例编号',
    'ALDCJR': '案例的创建人',
    'ALDSHR': '案例的审核人',
    'ALJRRQ': '案例加入日期',
    'ALFYCS': '案例复用次数',
    'ALYXCS': '案例有效次数',
    'DFAXGDPF': '对方案效果的评分',
    'DFAXGDMS': '对方案效果的描述',
    'BZ8': '备注8',

    'GZMLX':'工作面类型',
    'JTWZ':'具体位置',
    'RCL':'日产量',
    'ZXCD':'走向长度',
    'GZMCD':'工作面长度',
    'MCZRQX':'煤层自燃倾向性',
    'MCBZ':'煤尘爆炸倾向',
    'MCHD':'煤层厚度',
    'PJQJ':'平均倾角',
    'PJMS':'平均埋深',
    'JFXXS':'坚固性系数',
    'WSHL':'瓦斯含量',
    'TQXXS':'透气性系数',
    'ZDWSYL':'最大瓦斯压力',
    'CMGY':'采煤工艺',
    'DBGL':'顶板管理',
    'QQT':'其他'
}

meta_MKJB = {
    1:"乡镇煤矿",
    2:"地方重点煤矿",
    3:"国有重点煤矿"
}
meta_KJWSDJ = {
    1:"低瓦斯矿井",
    2:"高瓦斯矿井",
    3:"瓦斯突出矿井"
}

class CaseSaver(object):
    def __init__(self):
        pass
    
    def format_doc(self, raw):
        doc = {
            "SGALBH":raw['SGALBH'],
            "XQYXX":{
                'QYMC':raw['QYMC'],
                'QYXZ':raw['QYXZ'],
            },
            "XKJXX":{
                'MKJB':raw['MKJB'],
                'MKLX':raw['MKLX'],
                'WZYZ':raw['WZYZ'],
                'SPTG':raw['SPTG'],
                'SJSCNL1':raw['SJSCNL1'],
                'SJSCNL2':raw['SJSCNL2'],       
                'CYRYSL':raw['CYRYSL'],       
                'KJWSDJ':raw['KJWSDJ'],       
                'KJKCFS':raw['KJKCFS'],       
                'KJTFFS':raw['KJTFFS']                     
            },
            "XSGJBXX":{
                'SGSJ':raw['SGSJ'],
                'SGDD':raw['SGDD'],
                'SGLX':raw['SGLX'],
                'SGXZ':raw['SGXZ'],
            },
            "XSGDZSWTJ":{
                'DZGZFZCD':raw['DZGZFZCD'],
                'SGSWDZHJ':raw['SGSWDZHJ']
            },
            "XSGJCXX":{
                'CH4HL':raw['CH4HL'],
                'CO2HL':raw['CO2HL'],
                'COHL':raw['COHL'],
                'QTJCHS':raw['QTJCHS']
            },
            "XSGGC":"\n".join([l.strip() for l in raw['SGGCMSYW'].split()]),
            "XSGYY":{
                'ZJYY':raw['ZJYY'],
                'JJYY':raw['JJYY'],
                'RWYY':raw['RWYY'],
                'JXYY':raw['JXYY'],
                'GLYY':raw['GLYY'],
                'HJYY':raw['HJYY'],
            },
            ''
            'XSGJYCS':raw['SGJYCSYW'],
            'XSGSSXX':{
                'SWRS':raw['SWRS'],
                'SSRS':raw['SSRS'],
                'ZJJJSS':raw['ZJJJSS'],
                'JJJJSS':raw['JJJJSS'],
                'YJXYJB':raw['YJXYJB'],
                'YXFW':raw['YXFW']
            },
            'GZMLX':raw['GZMLX'],
            'SJSCNL2':raw['SJSCNL2'], 
            'JTWZ':raw['JTWZ'],
            'RCL':raw['RCL'],
            'ZXCD':raw['ZXCD'],
            'GZMCD':raw['GZMCD'],
            'MCZRQX':raw['MCZRQX'],
            'MCBZ':raw['MCBZ'],
            'MCHD':raw['MCHD'],
            'PJQJ':raw['PJQJ'],
            'PJMS':raw['PJMS'],
            'JFXXS':raw['JFXXS'],
            'WSHL':raw['WSHL'],
            'TQXXS':raw['TQXXS'],
            'ZDWSYL':raw['ZDWSYL'],
            'CMGY':raw['CMGY'],
            'DBGL':raw['DBGL'],
            'QQT':raw['QQT'],
            'ZQXDWSYCL':raw['ZQXDWSYCL'],
            'ZQJDWSYCL':raw['ZQJDWSYCL'],
            'XSGFFCS':raw['SGFFCSYW'],
            "TITLE":str(raw['SGSJ'])+str(raw['SGDD'])+str(raw['SGLX']),
        }

        doc['CONTENT'] = " \n ".join([str(i) for i in list(raw.values())])

        return doc

    def insert(self, _path):
        db_mongo = get_mongo_conn2coaldb()
        data = pd.read_excel(_path)
        for i in range(1,data.index.size):
            dd = data.iloc[i].to_dict()
            doc = self.format_doc(dd)
            db_mongo[mongo_collection_rawdata].insert_one(
                doc
            )
            print('done insert %s' % i)
            


def find_one(_id = ""):
    db_mongo = get_mongo_conn2coaldb()
    _id = ObjectId(_id)
    res = db_mongo[mongo_collection_rawdata].find_one({"_id":_id})
    return res
    


def insert_data():
    path = '../../data/coal_case.xlsx'
    cs = CaseSaver()
    cs.insert(path)

if __name__ == "__main__":
    insert_data()
    # print(find_one("5c90c720230b941089090b50"))

    
    
