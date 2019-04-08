import os, sys, time
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from monitor import monitor_api
from monitor import monitor_define
from pyknow import *
from xfacts import *
from gas_analysis import GasMonitorStatus

class TriggerEngine(KnowledgeEngine):

    def __init__(self, gas_analysis_obj):
        super().__init__()
        self.monitor_fact_dict = {}
        self.cur_status_fact = None

        self.gas_analysis_obj = gas_analysis_obj

    
    def init_data(self, _init_timestamp):
        # 初始化传感器事实
        self.__declare_monitor_fact(_init_timestamp)
        

    def __declare_monitor_fact(self, _init_timestamp):
        """
            declare fact for each monitor Fact
        """
        for mid in monitor_define.get_monitor_ids():
            temp_fact = XMonitorFact(mid=mid, val=0.0, val_pred=[],timestamp=_init_timestamp)
            self.monitor_fact_dict[mid] = self.declare(temp_fact)
        print('declare monitor fact done..')

    def update_monitor_value_fact(self, data_dict, _timestamp):
        for k,(v,pred_v) in data_dict.items():
            if k in self.monitor_fact_dict:
                temp_fact = self.monitor_fact_dict[k]
                self.monitor_fact_dict[k] = self.modify(temp_fact, val=float(v), val_pred=pred_v, timestamp=_timestamp)

    def real_run(self, data_dict, _timestamp):
        self.update_monitor_value_fact(data_dict, _timestamp=_timestamp)
        self.run()
        self.gas_analysis_obj.analysis()
        


    # 瓦斯超限
    @Rule(
        AS.monitor_fact << XMonitorFact(
            mid=MATCH.monitor_id, 
            val=MATCH.monitor_val,
            val_pred=MATCH.monitor_val_pred,
            timestamp = MATCH.timestamp
            ),
        TEST(
            lambda monitor_id, monitor_val,monitor_val_pred: \
                monitor_id in monitor_define.get_monitor_ids_by_type() \
                and monitor_val >= 0.1 
        )
    )
    def rule_gas_over(self, monitor_fact, monitor_id, monitor_val,monitor_val_pred, timestamp):
        gas_status_obj = GasMonitorStatus(monitor_id)
        gas_status_obj.timestamp = timestamp
        gas_status_obj.status_type = 'over_limit'
        gas_status_obj.monitor = monitor_define.get_monitor_by_id(monitor_id)
        gas_status_obj.activate_facts = [monitor_fact]
        self.gas_analysis_obj.update_gas_status(monitor_id, gas_status_obj)


    # 瓦斯预警
    @Rule(
        AS.monitor_fact << XMonitorFact(
            mid=MATCH.monitor_id, 
            val=MATCH.monitor_val,
            val_pred=MATCH.monitor_val_pred,
            timestamp = MATCH.timestamp
            ),
        TEST(
            lambda monitor_id, monitor_val,monitor_val_pred: \
                monitor_id in monitor_define.get_monitor_ids_by_type() \
                and monitor_val < 0.1
                and len(monitor_val_pred) > 0 
                and max(monitor_val_pred) >= 0.1
        )
    )
    def rule_gas_pred(self, monitor_fact, monitor_id, monitor_val,monitor_val_pred,timestamp):
        gas_status_obj = GasMonitorStatus(monitor_id)
        gas_status_obj.timestamp = timestamp
        gas_status_obj.status_type = 'pred_over_limit'
        gas_status_obj.monitor = monitor_define.get_monitor_by_id(monitor_id)
        gas_status_obj.activate_facts = [monitor_fact]
        for i,v in enumerate(monitor_val_pred):
            if v >= 0.1:
                gas_status_obj.pred_over_limit_index = i+1 #记录下到底是第几个开始超限了
                break
        self.gas_analysis_obj.update_gas_status(monitor_id, gas_status_obj)

    # 瓦斯正常
    @Rule(
        AS.monitor_fact << XMonitorFact(
            mid=MATCH.monitor_id, 
            val=MATCH.monitor_val,
            val_pred=MATCH.monitor_val_pred,
            timestamp = MATCH.timestamp
            ),
        TEST(
            lambda monitor_id, monitor_val,monitor_val_pred: \
                monitor_id in monitor_define.get_monitor_ids_by_type() \
                and monitor_val < 0.1 #没有超限
                and (len(monitor_val_pred)==0 or max(monitor_val_pred)<0.1) #没有预测值或者预测值小于阈值
        )
    )
    def rule_gas_normal(self, monitor_fact, monitor_id, monitor_val,monitor_val_pred,timestamp):
        gas_status_obj = GasMonitorStatus(monitor_id)
        gas_status_obj.timestamp = timestamp
        gas_status_obj.status_type = 'normal'
        gas_status_obj.monitor = monitor_define.get_monitor_by_id(monitor_id)
        gas_status_obj.activate_facts = [monitor_fact]
        self.gas_analysis_obj.update_gas_status(monitor_id, gas_status_obj)



if __name__ == "__main__":
    # print(xstatus_gas_over['sid'], xstatus_gas_over['description'])
    te = TriggerEngine()
    te.reset()
    init_timestamp = datetime.strptime('2017-09-18 00:00:00', '%Y-%m-%d %H:%M:%S')
    time_delta = timedelta(minutes=2)
    te.init_data(init_timestamp)
    cur_time = init_timestamp
    for i in range(20):
        data = monitor_api.fmd.get_cur_data(index=i)
        print('index=',i, 'time=', cur_time)
        cur_time = cur_time + time_delta
        te.update_monitor_value_fact(data,_timestamp=cur_time)

        # print(te.monitor_fact_dict)
        te.run()
        te.gas_analysis_obj.analysis()

    
    