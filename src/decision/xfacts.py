import os, sys, time
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from pyknow import *

XSTATUS_DEFINE = {
    'normal':{
        'sid':'normal',
        'descrip':'正常状态',
    },
    'gas_pred':{
        'sid':'gas_pred',
        'descrip':'瓦斯预警状态',
    },
    'gas_over':{
        'sid':'gas_over',
        'descrip':'瓦斯超限状态',
    },
}

class XStatusFact(Fact):
    sid = Field(str, default='normal')
    descrip = Field(str, default='正常状态')


class XMonitorFact(Fact):
    mid = Field(str)
    val = Field(float, default=0.0)
    val_pred = Field(list, default=[])
    timestamp = Field(datetime)

    


    


    
    