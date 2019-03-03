import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from monitor import monitor_api
from monitor import monitor_define
from pyknow import *
from xfacts import *
from xkernal_status import KERNAL_OBJ
from global_status import GLOBAL_STATUS


class GasMonitorStatus(object):
    def __init__(self, _monitor_id):
        """
        哪个传感器 什么状态 什么时间点 以及详细信息
        """
        self.monitor_id = _monitor_id #唯一标识该传感器
        self.timestamp = None
        self.status_type = None # 'normal' or 'pred_over_limit' or 'over_limit' or 'not_know'

        self.monitor = None
        self.activate_facts = None
        self.activate_rule = None #触发了哪条规则

class GasAnalysisEventType(object):
    NORMAL = "瓦斯浓度状态正常"
    PRED_LEVEL_1 = "局部瓦斯预警"
    PRED_LEVEL_2 = "工作面瓦斯预警"
    OVER_LEVEL_1 = "局部瓦斯超限"
    OVER_LEVEL_2 = "工作面瓦斯超限"

class GasAnalysisEvent(object):
    """
    瓦斯传感器综合评估结果事件
    """

    def __init__(self, _monitor_status_dict):
        self.monitor_status_dict = _monitor_status_dict

        self.pred_over_limit_list = []
        self.over_limit_list = []
        self.timestamp = None
        self.event_type = None
        self.generate_info()
        
    def generate_info(self):
        cur_timestamp_list = []
        for sid, status_obj in self.monitor_status_dict.items():
            if status_obj.status_type == 'pred_over_limit':
                self.pred_over_limit_list.append(status_obj)
            elif status_obj.status_type == 'over_limit':
                self.over_limit_list.append(status_obj)
            cur_timestamp_list.append(status_obj.timestamp)
        self.timestamp = max(cur_timestamp_list)

        # 开始确定当前的类型
        pred_num = len(self.pred_over_limit_list)
        over_num = len(self.over_limit_list)

        if over_num == 0: # 非超限问题
            if pred_num == 0: # 无预警问题
                self.event_type = GasAnalysisEventType.NORMAL
            
            elif pred_num == 1: #局部超限
                self.event_type = GasAnalysisEventType.PRED_LEVEL_1
            elif pred_num > 1:
                self.event_type = GasAnalysisEventType.PRED_LEVEL_2
        elif over_num == 1:
            self.event_type = GasAnalysisEventType.OVER_LEVEL_1
        else:
            self.event_type = GasAnalysisEventType.OVER_LEVEL_2
        return 

    def get_title(self):
        return self.event_type

    def get_detail(self):
        pred_monitor_name = [obj.monitor['NAME'] for obj in self.pred_over_limit_list]
        over_monitor_name = [obj.monitor['NAME'] for obj in self.over_limit_list]
        content = ""
        if len(over_monitor_name) > 0:
            content += ("%s处监测到瓦斯浓度超限.") % ','.join(over_monitor_name)
        if len(pred_monitor_name) > 0:
            content += ("%s处瓦斯浓度预测有超限倾向.") % ','.join(pred_monitor_name)

        content += "请及时做好各项应急措施."
        return content
   

class Suggestion(object):
    def __init__(self):
        pass


class GasAnalysis(object):
    """
    monitorstatus => event + suggenstions 
    and decide whether push to kernal_obj or not 
    """
    def __init__(self):
        
        self.gas_monitor_ids = list(monitor_define.get_monitor_ids_by_type())

        self.reserve_status = {} #id -> status_obj
        self.reserve_status_update = False
        self.current_status = {}  # id -> status_obj
        
        self.result_event = None
        self.suggestions = []

    def update_gas_status(self, gasid, status_obj):
        assert gasid in self.gas_monitor_ids
        self.current_status[gasid] = status_obj
        # 查看是否与上次状态发生了变化，如果发生了，则进行替换，同时确认此次应该进行更新
        if (gasid not in self.reserve_status) or (self.reserve_status[gasid].status_type != status_obj.status_type):
            self.reserve_status[gasid] = status_obj
            self.reserve_status_update = True


    def analysis(self):
        """
        """
        if len(self.current_status) == 0:
            print('[GasAnalysis]: no current gas status..')
            return 
        self.result_event = GasAnalysisEvent(self.current_status)
        print(self.result_event.get_title(), self.result_event.get_detail())
        
       
gas_analysis_obj = GasAnalysis()

        

        
        



        


