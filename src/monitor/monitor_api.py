# author charnix@pku.edu.cn

#本文件提供数据支持的api

#######具体数据包括##########
#   瓦斯
#   风速
#   CO
#   CO2
#   O2
###########################
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

import numpy as np
import pandas as pd
from datetime import datetime

from monitor_define import get_monitor_ids


class MonitorData():
    def __init__(self):
        pass


    def get_cur_data(self):
        pass

    

#真实世界的模拟器，时间与真实世界相对应
class FileMonitorData(MonitorData):
    def __init__(self, path, init_time=None, inter=120):
        """
        path: data is pd.DataFrame
        inter:时间间隔 单位 秒
        """
        self.path = path
        self.data = pd.read_csv(path).reset_index(drop=True)
        if not init_time:
            self.init_time = datetime.now()
        else:
            self.init_time = init_time
        self.inter = inter
        
    def datetime2index(self, dt_obj):
        """
        输入一个datetime对象，根据时间对象，返回对应的数据的index(pandas number index)
        """
        _size = self.data.index.size
        _total = (dt_obj - self.init_time).seconds // self.inter
        return _total % _size

    def get_next_index(self, cur_index, next_window=5):
        _size = self.data.index.size
        res = []
        for i in range(cur_index+1, cur_index+next_window+1):
            res.append(i % _size)
        return res

    def get_last_index(self, cur_index, last_window=10):
        res = []
        for i in range(last_window,0,-1):
            res.append(cur_index - i)
        return res

    def get_cur_data(self, index=None, cur_time=None, next_window=5):
        """
        优先使用index, 如果没有提供index则使用cur_time
        """
        if  index:
            index = index % self.data.index.size
        elif cur_time:
            index = self.datetime2index(cur_time)
        else:
            index = 0
        next_index_list = self.get_next_index(index, next_window=next_window)
        data = self.data.iloc[index,:].to_dict()
        next_data = self.data.iloc[next_index_list,:]
        # print('next_data=',next_data)
        res = {}
        for sid in get_monitor_ids():
            assert sid in data and sid in next_data
            res[sid] = (data[sid],list(next_data[sid]))
        return res

    def get_monitor_data_by_id_and_time(self, monitor_id, cur_index, last_window, next_window):
        cur_index = cur_index % self.data.index.size
        all_index = self.get_last_index(cur_index, last_window) + [cur_index] + self.get_next_index(cur_index,next_window)
        # print('all_index', all_index)
        data = self.data.iloc[all_index, :]
        return list(data[monitor_id])


    # 注意，该函数没有返回预测值
    # def get_cur_data_specific(self, cur_time=datetime.now(), last_window=5, method='mean'):
    #     index = self.datetime2index(cur_time)
    #     start_index = index - last_window
    #     data = self.data.iloc[start_index:index,:]
    #     # print(data.index.size)
    #     data = getattr(data,method)()
    #     res = {}
    #     for sid in get_monitor_ids():
    #         assert sid in data
    #         res[sid] = data[sid]
    #     return res

