import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
from decision.gas_analysis import GasAnalysisEventType, SuggenstionType
from launch import time_delta


def suggest_electronic(gas_analysis_obj):
    """
    原则上该函数需要通过分析当前瓦斯情况，来进行断电预告，由于本文研究重点不在此处，因此直接返回
    """
    gas_analysis_event = gas_analysis_obj.result_event
    if gas_analysis_event.event_type == GasAnalysisEventType.OVER_LEVEL_2:
        title = "断开W15117工作面电源"
        content = "断开后，W15117工作面采煤机等动力电源将丧失。建议进行断电操作。"
    else:
        title = "当前状态尚不需要进行断电操作"
        content = "断开后，W15117工作面采煤机等动力电源将丧失。建议谨慎操作。"
    res = {
        "title":title,
        "content":content
    }
    return res

    