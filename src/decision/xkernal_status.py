import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))

from xfacts import *



# 过程: 专家系统通过监测数据，自动触发规则，规则后件规定了在此种情况下，封装当前异常状况xecept对象（主要是数据对象，用于承载数据），
# 并给出当前状况下的建议，将异常和建议都加入到xkernal对象中, 异常list和建议list可以看做是随着时间线的流式系统，不过当修改xstatus时，则会进行清空，重新进行建议决策






class XKernal(object):
    def __init__(self):
        self.xstatus = None # status对象，描述当前的总结性状态信息，如正常状态、瓦斯超限预警、瓦斯超限
        self.event_infos = [] #异常信息，用于修改状态以来，已经收集到的异常信息
        self.suggestions = [] #当前的建议集合

        self.is_update = False #数据是否进行了更新，用于前端系统展示更新监测

    def update_status(self, new_status):
        """
        更新状态，被专家系统调用，修改当前状态，并同时添加新状态下基础的异常信息已经相关基础决策建议
        """
        self.xstatus = new_status
        # clear excepts and suggestions
        self.except_infos = []
        self.suggestions = []
        # change update to True
        self.is_update = True

    def insert_except(self):
        """
        添加新的异常信息，一般被专家系统调用，加入新的异常
        """
        pass


    def insert_suggestion(self):
        """
        添加新的建议信息，一般被专家系统调用，加入新的建议
        """
        pass


    def trans_data(self):
        """
        将对象转化为对应的可用于传输的信息，用于前端展示
        """
        pass
        


KERNAL_OBJ = XKernal()
