import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from monitor import monitor_api
from monitor import monitor_define
from pyknow import *
from xfacts import *

from xlog.xlog import xlogger,LogLevel

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

    def get_lonlat(self):
        return self.monitor['POS']['LON_LAT']

    def trans_status_type(self):
        if self.status_type == "normal":
            return "正常"
        elif self.status_type == "pred_over_limit":
            return "预计即将超限"
        elif self.status_type == "over_limit":
            return "超限"
        else:
            return "处于未知状态"
    
    def get_monitor_value(self):
        return self.activate_facts[0].get('val')

    def get_location(self):
        return self.monitor['POS']['TEXT']

    def trans_for_log(self):
        title = "%s工作面%s状态[%s]" % (self.monitor['POS']['WF'], self.monitor['NAME'], 
                                    self.trans_status_type())
        content = "传感器编号:%s, 名称:%s,  当前状态变:%s, 当前浓度:%s, 具体位置: %s" % ( 
                                    self.monitor_id, self.monitor['NAME'],self.trans_status_type(), self.get_monitor_value(),self.monitor['POS']['TEXT'] )
        return title, content





class AnalysisEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.analysis_event = None

    def analysis(self, _monitor_status_dict):
        self.reset()
        self.pred_over_limit_list = []
        self.over_limit_list = []
        self.normal_list = []

        cur_timestamp_list = []
        for sid, status_obj in _monitor_status_dict.items():
            if status_obj.status_type == 'pred_over_limit':
                self.pred_over_limit_list.append(status_obj)
            elif status_obj.status_type == 'over_limit':
                self.over_limit_list.append(status_obj)
            else:
                self.normal_list.append(status_obj)
            cur_timestamp_list.append(status_obj.timestamp)
        self.timestamp = max(cur_timestamp_list)

        # 开始确定当前的类型
        pred_num = len(self.pred_over_limit_list)
        over_num = len(self.over_limit_list)
        
        abnormal_pred_num_fact = self.declare(XABNORMALMonitorNum(abnormal_type='pred_over_limit', 
                                    val=pred_num,
                                    timestamp = self.timestamp))
        abnormal_over_num_fact = self.declare(XABNORMALMonitorNum(abnormal_type='over_limit', 
                                    val=over_num,
                                    timestamp = self.timestamp))
        
        self.run()
        return self.analysis_event


    def __get_content(self):
        pred_monitor_name = [obj.monitor['NAME'] for obj in self.pred_over_limit_list]
        over_monitor_name = [obj.monitor['NAME'] for obj in self.over_limit_list]
        content = []
        if len(over_monitor_name) > 0:
            content.append(("W15117工作面监测到%s处瓦斯超限，其中包括%s。") % (len(over_monitor_name),','.join(over_monitor_name)))
        if len(pred_monitor_name) > 0:
            content.append(("W15117工作面监测到%s处瓦斯浓度预测有超限倾向，其中包括%s。") % (len(pred_monitor_name) ,','.join(pred_monitor_name)))
        if len(content) == 0:
            content.append("当前无明显异常情况。")
        else:
            content.append('请依据参考系统提供的建议及时做好相应处置。')
        return content

    def update_analysis_event(self, event_type, timestamp):
        gas_event = GasAnalysisEvent()
        gas_event.timestamp = timestamp
        gas_event.event_type = event_type

        gas_event.title = gas_event.event_type 
        gas_event.content = self.__get_content()
        gas_event.over_limit_list = self.over_limit_list[:]
        gas_event.pred_over_limit_list = self.pred_over_limit_list[:]
        gas_event.normal_list = self.normal_list[:]
        self.analysis_event = gas_event   #update gas_event


    # 瓦斯超限状态
    @Rule(
        AS.pred_num_fact << XABNORMALMonitorNum(
            abnormal_type=MATCH.abnormal_type, 
            val=MATCH.val,
            timestamp = MATCH.timestamp
            ),
        TEST(
            lambda abnormal_type, val, timestamp: \
               abnormal_type == 'over_limit' and \
               val > 0
        )
    )
    def rule_status_gas_over(self, val, timestamp):
        print('activate gas over...')
        self.update_analysis_event(GasAnalysisEventType.OVER_LEVEL_2, timestamp)

    # 判定工作面预警状态
    @Rule(
        AS.over_num_fact << XABNORMALMonitorNum(
            abnormal_type=MATCH.abnormal_type1, 
            val=MATCH.val1,
            timestamp = MATCH.timestamp1
            ),
        TEST(
            lambda abnormal_type1, val1, timestamp1: \
               abnormal_type1 == 'over_limit' and \
               val1 == 0
        ),
        AS.pred_num_fact << XABNORMALMonitorNum(
            abnormal_type=MATCH.abnormal_type2, 
            val=MATCH.val2,
            timestamp = MATCH.timestamp2
            ),
        TEST(
            lambda abnormal_type2, val2, timestamp2: \
               abnormal_type2 == 'pred_over_limit' and \
               val2 > 0
        )
    )
    def rule_status_gas_pred(self,  val1, timestamp1, val2, timestamp2):
        print('activate gas pred...')
        timestamp = max(timestamp1, timestamp2)
        self.update_analysis_event(GasAnalysisEventType.PRED_LEVEL_2, timestamp)


# 瓦斯正常状态
    @Rule(
        AS.over_num_fact << XABNORMALMonitorNum(
            abnormal_type=MATCH.abnormal_type1, 
            val=MATCH.val1,
            timestamp = MATCH.timestamp1
            ),
        TEST(
            lambda abnormal_type1, val1, timestamp1: \
               abnormal_type1 == 'over_limit' and \
               val1 == 0
        ),
        AS.pred_num_fact << XABNORMALMonitorNum(
            abnormal_type=MATCH.abnormal_type2, 
            val=MATCH.val2,
            timestamp = MATCH.timestamp2
            ),
        TEST(
            lambda abnormal_type2, val2, timestamp2: \
               abnormal_type2 == 'pred_over_limit' and \
               val2 == 0
        )
    )
    def rule_status_gas_normal(self, val1, timestamp1, val2, timestamp2):
        print('activate gas normal...')
        timestamp = max(timestamp1, timestamp2)
        self.update_analysis_event(GasAnalysisEventType.NORMAL, timestamp)



class GasAnalysisEvent(object):
    """
    瓦斯传感器综合评估结果事件
    """

    def __init__(self):
        self.timestamp = None
        self.event_type = None
        self.title = None
        self.content = None
        self.normal_list = []
        self.over_limit_list = []
        self.pred_over_limit_list = []

   
    def get_title(self):
        return self.title

    def get_detail(self):
        return self.content
   


    def get_center_zoom(self):
        center = [106213.5183083,69317.10151376]
        zoom = 5
        over_list = self.pred_over_limit_list[:] + self.over_limit_list[:]
        if len(over_list) == 0:
            center = [106213.5183083,69317.10151376]
            zoom = 5
        else:
            xlist = [x.get_lonlat()[1] for x in over_list]
            ylist = [x.get_lonlat()[0] for x in over_list]
            cx = sum(xlist) / len(over_list)
            cy = sum(ylist) / len(over_list)
            xmin,xmax,ymin,ymax = min(xlist),max(xlist),min(ylist),max(ylist)
            ll = ((xmax-xmin)**2 + (ymax-ymin)**2)**0.5
            if ll < 3:
                zoom = 13
            elif ll < 10:
                zoom = 11
            else:
                zoom = 5
            center = [cx, cy]
        res = {
            "center":center,
            "zoom":zoom
        }
        return res

    def get_data(self):
        res = []
        def get_item(status_obj):
            temp = {
                "ID": status_obj.monitor_id,
                "Data": status_obj.get_monitor_value(),
                "X": status_obj.get_lonlat()[1],
                "Y": status_obj.get_lonlat()[0],
                "Status":status_obj.status_type,
                "text":"<table class='table'> \
                            <tr class='active'> \
                                <td> 时间 </td> \
                                <td> %s </td> \
                            </tr> \
                            <tr class='active'> \
                                <td> ID </td> \
                                <td> %s </td> \
                            </tr> \
                            <tr class='active'> \
                                <td> 位置 </td> \
                                <td> %s </td> \
                            </tr> \
                            <tr class='active'> \
                                <td> 浓度 </td> \
                                <td> %s </td> \
                            </tr> \
                            <tr class='active'> \
                                <td> 状态 </td> \
                                <td> <h4>%s</h4> </td> \
                            </tr> \
                        </table>" % (self.timestamp, status_obj.monitor_id,status_obj.get_location(),status_obj.get_monitor_value(),status_obj.trans_status_type())
            }
            return temp
        for item in self.normal_list + self.pred_over_limit_list + self.over_limit_list:
            res.append(get_item(item))
        return res

    def get_area(self):
        if len(self.over_limit_list) > 0:
            return [[68596.008,105991.888],[68596.008,106214.702],[70076.661,106214.702],[70085.216,105989.797]]
        else:
            return []


class SuggenstionType(object):
    SUGGESTION_ORGANIZE = 'suggestion_organize'
    SUGGESTION_ELECTONIC = 'suggestion_electronic'
    SUGGESTION_ESCAPE = 'suggestion_escape'
    SUGGESTION_AIR = 'suggestion_air'
    SUGGESTION_SIMPLE_ACTION = 'suggestion_simple_action' #例如一些提醒，修改状态量
    
class Suggestion(object):
    def __init__(self):
        pass


class SimpleSuggestion(Suggestion):
    def __init__(self):
        self.suggestion_id = None 
        self.suggenstion_type = None
        self.level = 'danger' #与boostrap的颜色相对应
        self.title = ""
        self.description = ""
        self.activate_title = ""
        self.execute_func = None

    def execute(self, gas_analysis_obj, xlogger, timestamp, *args, **kwargs):
        return self.execute_func(self, gas_analysis_obj, xlogger, timestamp, *args, **kwargs)




class GasSuggenstionAnalysis(object):
    def __init__(self, _gas_event=None, _global_status=None):
        self.gas_event = _gas_event
        self.global_status= _global_status
        self.id2suggestion = {}
    
    def get_suggestion_info(self, sug_id):
        if sug_id not in self.id2suggestion:
            print('can not find suggestion of %s' % sug_id)
            return None
        sug_obj = self.id2suggestion[sug_id]
        return sug_obj
        


class SuggestEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.gas_suggest_obj = None

    def suggest(self, _gas_event, _global_status):

        self.reset()

        self.gas_event = _gas_event
        self.global_status= _global_status
        
        cur_event_type = _gas_event.event_type
        cur_status = _global_status.global_status_period
        gas_event_type_fact = self.declare(XAnalysisEventTypeFact(analysis_event_type=cur_event_type))
        status_fact = self.declare(XStatusFact(sid=cur_status))
        
        self.run()
        return self.gas_suggest_obj

    def generate_suggest(self, id2suggestion):
        gas_suggest_obj = GasSuggenstionAnalysis()
        gas_suggest_obj.id2suggestion = id2suggestion
        gas_suggest_obj.gas_event = self.gas_event
        gas_suggest_obj.global_status = self.global_status
        self.gas_suggest_obj = gas_suggest_obj


    #正常状态
    @Rule(
        AS.analysis_event_type_fact << XAnalysisEventTypeFact(
             analysis_event_type=MATCH.cur_event_type
            ),
        AS.status_fact << XStatusFact(
            sid=MATCH.cur_status
            ),
        TEST(
            lambda cur_event_type, cur_status: \
               cur_status == 'normal' and \
               (cur_event_type in [GasAnalysisEventType.NORMAL])
        )
    )
    def suggest_when_normal(self):
        id2suggestion = {}
        simple_sug_obj = SimpleSuggestion()
        my_sug_id_0 = 'gas_suggestion_everything_is_ok_0'
        simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_SIMPLE_ACTION
        simple_sug_obj.suggestion_id = my_sug_id_0
        simple_sug_obj.level = 'success'
        simple_sug_obj.title = "正常状态"
        simple_sug_obj.description = "当前无需进行任何应急处置..."
        id2suggestion[my_sug_id_0] = simple_sug_obj
        self.generate_suggest(id2suggestion)
        
    
    @Rule(
        AS.analysis_event_type_fact << XAnalysisEventTypeFact(
             analysis_event_type=MATCH.cur_event_type
            ),
        AS.status_fact << XStatusFact(
            sid=MATCH.cur_status
            ),
        TEST(
            lambda cur_event_type, cur_status: \
               cur_status == 'normal' and \
               (cur_event_type in [GasAnalysisEventType.PRED_LEVEL_1 , GasAnalysisEventType.PRED_LEVEL_2])
        )
    )
    def suggest_when_normal_pred(self):
        id2suggestion = {}
        my_sug_id_0 = "gas_suggestion_be_careful_about_the_gas_pred_over_limit_0"
        simple_sug_obj = SimpleSuggestion()
        simple_sug_obj.suggestion_id = my_sug_id_0
        simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_SIMPLE_ACTION
        simple_sug_obj.level = 'warning'
        simple_sug_obj.title = "加强注意"
        simple_sug_obj.description = "建议加强对该位置处瓦斯检查..."
        id2suggestion[my_sug_id_0] = simple_sug_obj
        self.generate_suggest(id2suggestion)
    

    @Rule(
        AS.analysis_event_type_fact << XAnalysisEventTypeFact(
             analysis_event_type=MATCH.cur_event_type
            ),
        AS.status_fact << XStatusFact(
            sid=MATCH.cur_status
            ),
        TEST(
            lambda cur_event_type, cur_status: \
               cur_status == 'normal' and \
               (cur_event_type in [GasAnalysisEventType.OVER_LEVEL_1 ,GasAnalysisEventType.OVER_LEVEL_2])
        )
    )
    def suggest_when_normal_over(self):
        id2suggestion = {}
        my_sug_id_0 = "gas_suggestion_gas_over_limit_0"
        simple_sug_obj = SimpleSuggestion()
        simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_SIMPLE_ACTION
        simple_sug_obj.suggestion_id = my_sug_id_0
        simple_sug_obj.level = 'danger'
        simple_sug_obj.title = "应急处置"
        simple_sug_obj.description = "建议立即启动瓦斯超限应急处置方案,启动后系统将进入应急状态并进行实时决策支持..."
        simple_sug_obj.activate_title = "启动应急处置"
        def execute_func(sug_obj, gas_analysis_obj, xlogger,timestamp, *args, **kwargs):
            gas_analysis_obj.set_global_status('global_status_period','on_urgent')
            xlogger.append_log(timestamp, '启动应急处置','系统开始进入应急状态...')
            print(sug_obj.suggestion_id)
        simple_sug_obj.execute_func = execute_func
        id2suggestion[my_sug_id_0] = simple_sug_obj
        self.generate_suggest(id2suggestion)
    


    @Rule(
        AS.analysis_event_type_fact << XAnalysisEventTypeFact(
             analysis_event_type=MATCH.cur_event_type
            ),
        AS.status_fact << XStatusFact(
            sid=MATCH.cur_status
            ),
        TEST(
            lambda cur_event_type, cur_status: \
               cur_status == 'on_urgent' and \
               (cur_event_type in [GasAnalysisEventType.NORMAL])
        )
    )
    def suggest_when_urgent_normal(self):
        id2suggestion = {}
        simple_sug_obj = SimpleSuggestion()
        my_sug_id_0 = 'gas_suggestion_urgent_is_ok_0'
        simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_SIMPLE_ACTION
        simple_sug_obj.suggestion_id = my_sug_id_0
        simple_sug_obj.level = 'info'
        simple_sug_obj.title = "恢复生产"
        simple_sug_obj.description = "应急处置完成,监测到指标已经恢复正常,建议关闭应急状态，恢复生产与正常监测监控状态..."
        simple_sug_obj.activate_title = "恢复正常监测状态"
        def execute_func(sug_obj, gas_analysis_obj,xlogger,timestamp, *args, **kwargs):
            gas_analysis_obj.set_global_status('global_status_period','normal')
            xlogger.append_log(timestamp, '确认恢复正常状态','系统开始恢复到正常监测状态...')
            # print(sug_obj.suggestion_id)
        simple_sug_obj.execute_func = execute_func
        id2suggestion[my_sug_id_0] = simple_sug_obj
        self.generate_suggest(id2suggestion)


    @Rule(
        AS.analysis_event_type_fact << XAnalysisEventTypeFact(
             analysis_event_type=MATCH.cur_event_type
            ),
        AS.status_fact << XStatusFact(
            sid=MATCH.cur_status
            ),
        TEST(
            lambda cur_event_type, cur_status: \
               cur_status == 'on_urgent' and \
               (cur_event_type in [GasAnalysisEventType.OVER_LEVEL_1 ,GasAnalysisEventType.OVER_LEVEL_2, 
                        GasAnalysisEventType.PRED_LEVEL_1 , GasAnalysisEventType.PRED_LEVEL_2])
        )
    )
    def suggest_when_urgent_over(self):
        id2suggestion = {}
        # 断电
        my_sug_id_0 = "gas_suggestion_over_limit12_electronic_0"
        simple_sug_obj = SimpleSuggestion()
        simple_sug_obj.suggestion_id = my_sug_id_0
        simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_ELECTONIC
        simple_sug_obj.level = 'danger'
        simple_sug_obj.title = "立即断电"
        simple_sug_obj.description = "建议立即启动电力分析，并进行断电操作..."
        simple_sug_obj.activate_title = "启动应急断电分析"
        id2suggestion[my_sug_id_0] = simple_sug_obj

        # 人员撤离
        my_sug_id_1 = "gas_suggestion_over_limit12_escape_1"
        simple_sug_obj = SimpleSuggestion()
        simple_sug_obj.suggestion_id = my_sug_id_1
        simple_sug_obj.suggenstion_type = SuggenstionType.SUGGESTION_ESCAPE
        simple_sug_obj.level = 'danger'
        simple_sug_obj.title = "组织撤离"
        simple_sug_obj.description = "建议立即启动人员逃生系统，并组织人员撤离..."
        simple_sug_obj.activate_title = "启动人员逃生系统"
        id2suggestion[my_sug_id_1] = simple_sug_obj

        self.generate_suggest(id2suggestion)



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
        
        self.analysis_engine =  AnalysisEngine()
        self.result_event = None
        self.last_result_event = None  #用于记录时间线Log

        self.suggest_engine = SuggestEngine()
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
            if gasid in self.reserve_status:
                #如果发生了变化，则需要记录内容
                cur_time = status_obj.timestamp
                title, content = status_obj.trans_for_log()
                xlogger.append_log(status_obj.timestamp,title, content,log_level=LogLevel.WARNING)
                # xlogger.print_log()

    
    def analysis(self):
        """
        """
        if len(self.current_status) == 0:
            print('[GasAnalysis]: no current gas status..')
            return 
        self.result_event = self.analysis_engine.analysis(self.current_status)

        #如果本次发生了变化则对analysis的综合结果记录时间线
        if not self.last_result_event or self.last_result_event.event_type!=self.result_event.event_type:
            if self.last_result_event:
                cur_time = self.result_event.timestamp
                title = "综合分析:[%s],之前状态为[%s]" % (self.result_event.get_title(), self.last_result_event.get_title())
                content = " ".join(self.result_event.get_detail())
                xlogger.append_log(cur_time, title, content,log_level=LogLevel.DANEGR)
            self.last_result_event = self.result_event 
            # xlogger.print_log()

        self.suggestion_analysis_obj =self.suggest_engine.suggest(self.result_event, self.global_status)
        self.update = True
        print('后台结果: ', self.result_event.get_title())

        
       


        

        
        



        


