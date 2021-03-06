import os, sys, time
import threading
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))


from decision.xengine import TriggerEngine
from decision.gas_analysis import GasAnalysis
import monitor_api

# time system
cur_index, cur_time = 0, datetime.strptime('2017-10-18 00:00:00', '%Y-%m-%d %H:%M:%S')
time_delta = timedelta(minutes=2)
last_time_index = -1

# monitor data
path_data = os.path.join(os.path.dirname(__file__) ,'../../data/gas_censor.csv')
fmd = monitor_api.FileMonitorData(path_data, init_time=cur_time)

# global status
class GlobalStatus(object):
    def __init__(self):
        self.global_status_period = 'normal' # normal or on_urgent

global_status = GlobalStatus()

# analysis object
gas_analysis_obj = GasAnalysis(global_status)


def get_cur_time():
    return (not cur_index==last_time_index), cur_index, cur_time



def index2time(index_list):
    global cur_index, cur_time, time_delta
    res = []
    for index in index_list:
        res.append(cur_time + ((index - cur_index) * time_delta))
    return res

def get_gas_analysis_obj():
    global gas_analysis_obj
    return gas_analysis_obj

def launch_trigger_engine(gas_analysis_obj):
    global fmd, time_delta
    global cur_index, cur_time, last_time_index
    te = TriggerEngine(gas_analysis_obj)
    te.init_data(cur_time)
    while True:
        data = fmd.get_cur_data(index=cur_index)
        print('index=',cur_index, 'time=', cur_time)
        te.real_run(data, _timestamp=cur_time)
        time.sleep(3)
        cur_time += time_delta
        last_time_index = cur_index
        cur_index += 1


def launch():
    threading.Thread(target=launch_trigger_engine, kwargs= {"gas_analysis_obj":gas_analysis_obj}).start()
    # launch_trigger_engine(time_delta)
    

    

if __name__ == "__main__":
    launch()
    # print(index2time([-3,-2,-1,0,1,2,3]))