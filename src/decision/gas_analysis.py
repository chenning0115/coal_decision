import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from monitor import monitor_api
from monitor import monitor_define
from pyknow import *
from xfacts import *


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

        self.pred_over_limit_index = 0



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
   



class SuggenstionType(object):
    SUGGESTION_ORGANIZE = 'suggestion_organize'
    SUGGESTION_ELECTONIC = 'suggestion_electronic'
    SUGGESTION_AIR = 'suggestion_air'
    SUGGESTION_SIMPLE_ACTION = 'suggestion_simple_action' #例如一些提醒，修改状态量
    SUGGESTION_NORMAL = "suggestion_normal"
    
class Suggestion(object):
    def __init__(self):
        pass


class SimpleSuggestion(Suggestion):
    def __init__(self):
        self.suggestion_id = None 
        self.suggenstion_type = None #类型 组织，断电，逃生，加大风量等
        self.args_dict = {}
        self.level = 'danger' #与boostrap的颜色相对应
        self.title = ""
        self.description = ""
        self.activate_title = ""


class GasSuggenstionAnalysis(object):
    def __init__(self, _gas_event, _global_status):
        self.gas_event = _gas_event
        self.global_status= _global_status
        self.id2suggestion = {}
        self.suggest()

        for sid, sg in self.id2suggestion.items():
            print(sid, sg.title)

    def suggest(self):
        event_type = self.gas_event.event_type
        if self.global_status.global_status_period == 'normal':
            if event_type == GasAnalysisEventType.NORMAL:
                my_sug_id_0 = 'gas_suggestion_everything_is_ok_0'
                simple_sug_obj = SimpleSuggestion()
                simple_sug_obj.suggestion_id = my_sug_id_0
                simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_NORMAL
                simple_sug_obj.level = 'success'
                simple_sug_obj.title = "正常状态"
                simple_sug_obj.description = "当前无需进行应急处置..."
                self.id2suggestion[my_sug_id_0] = simple_sug_obj

            elif event_type in [GasAnalysisEventType.PRED_LEVEL_1 , GasAnalysisEventType.PRED_LEVEL_2]:
                my_sug_id_0 = "gas_suggestion_be_careful_about_the_gas_pred_over_limit_0"
                simple_sug_obj = SimpleSuggestion()
                simple_sug_obj.suggestion_id = my_sug_id_0
                simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_SIMPLE_ACTION
                simple_sug_obj.level = 'warning'
                simple_sug_obj.title = "加强注意"
                simple_sug_obj.description = "建议加强对该位置处瓦斯检查..."
                simple_sug_obj.activate_title = ""
                self.id2suggestion[my_sug_id_0] = simple_sug_obj

            elif event_type in [GasAnalysisEventType.OVER_LEVEL_1 ,GasAnalysisEventType.OVER_LEVEL_2]:
                my_sug_id_0 = "gas_suggestion_gas_over_limit_0"
                simple_sug_obj = SimpleSuggestion()
                simple_sug_obj.suggestion_id = my_sug_id_0
                simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_SIMPLE_ACTION
                simple_sug_obj.level = 'danger'
                simple_sug_obj.title = "应急处置"
                simple_sug_obj.description = "建议立即启动<瓦斯超限>应急处置方案,启动后系统将进入应急状态并进行实时决策支持..."
                simple_sug_obj.activate_title = "启动应急处置"
                self.id2suggestion[my_sug_id_0] = simple_sug_obj
            else:
                pass

        elif self.global_status.global_status_period == 'on_urgent':
            if event_type == GasAnalysisEventType.NORMAL:
                pass

            elif event_type in [GasAnalysisEventType.PRED_LEVEL_1 , GasAnalysisEventType.PRED_LEVEL_2,
                    GasAnalysisEventType.OVER_LEVEL_1 ,GasAnalysisEventType.OVER_LEVEL_2]:
                pass
            else:
                pass
    
    def get_suggestion_info(self, sug_id):
        if sug_id not in self.id2suggestion:
            print('can not find suggestion of %s' % sug_id)
            return None
        sug_obj = self.id2suggestion[sug_id]
        return sug_obj
        

class GasAnalysis(object):
    """
    monitorstatus => event + suggenstions 
    and decide whether push to kernal_obj or not 
    """
    def __new__(cls, args):
        if not hasattr(cls, 'instance'):
            cls.instance = super(GasAnalysis, cls).__new__(cls)
        return cls.instance

    def __init__(self, global_status):
        
        self.gas_monitor_ids = list(monitor_define.get_monitor_ids_by_type())

        self.global_status = global_status

        self.reserve_status = {} #id -> status_obj
        self.reserve_status_update = False
        self.current_status = {}  # id -> status_obj
        
        self.result_event = None
        self.suggestion_analysis_obj = None
        self.update = False

    def set_global_status(self, name, value):
        setattr(self.global_status, name, value)
        self.analysis()

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
        self.suggestion_analysis_obj = GasSuggenstionAnalysis(self.result_event, self.global_status)
        self.update = True
        print('后台结果: ', self.result_event.get_title())

        
       


        

        
        



        


