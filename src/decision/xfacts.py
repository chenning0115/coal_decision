import os, sys, time
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pyknow import *


class GasAnalysisEventType(object):
    NORMAL = "瓦斯浓度状态正常"
    PRED_LEVEL_1 = "局部瓦斯预警"
    PRED_LEVEL_2 = "工作面瓦斯预警"
    OVER_LEVEL_1 = "局部瓦斯超限"
    OVER_LEVEL_2 = "工作面瓦斯超限"


class XStatusFact(Fact):
    sid = Field(str, default='normal')  #just normal or on_urgent


class XMonitorFact(Fact):
    mid = Field(str)
    val = Field(float, default=0.0)
    val_pred = Field(list, default=[])
    timestamp = Field(datetime)

class XABNORMALMonitorNum(Fact):
    abnormal_type = Field(str) #pred_over_limit over_limit
    val = Field(int, default=0)
    timestamp = Field(datetime)

class XAnalysisEventTypeFact(Fact):
    analysis_event_type = Field(str, default=GasAnalysisEventType.NORMAL)
    


    


    
    