import os, sys, time
import datetime,json
sys.path.append(os.path.join(os.path.dirname(__file__) ,'.'))
sys.path.append(os.path.join(os.path.dirname(__file__) ,'..'))




class LogType(object):
    LOGTYPE_MONITOR = "监控状态"
    LOGTYPE_ANALYSIS = "综合分析"
    LOGTYPE_ACTION = "执行操作"

class LogLevel(object):
    NORMAL = "success"
    WARNING = "warning"
    DANEGR = "danger"
    

class LogItem(object):
    def __init__(self, _log_time, _log_type, _title, _content, _log_level):
        self.log_time = _log_time
        self.log_type = _log_type
        self.title = _title
        self.content = _content
        self.log_level = _log_level
    
    def get_date(self):
        return self.log_time.strftime("%Y-%m-%d")

    def get_time(self):
        return self.log_time.strftime("%H:%M")
    
    def get_title(self):
        if self.log_level:
            return "<p class='text-%s'>%s</p>" % (self.log_level, self.title)
        else:
            return self.title
    def get_content(self):
        if self.log_level:
            return "<p class='text-%s'>%s</p>" % (self.log_level, self.content)
        else:
            return self.content



class XLogger(object):
    def __init__(self, path_temp):
        self.path_save = path_temp
        self.log_list = []

    def append_log(self, log_time,  log_title="", log_content="", log_type=None, log_level=LogLevel.NORMAL):
        temp_item = LogItem(log_time, log_type, log_title, log_content, log_level)
        self.log_list.append(temp_item)

    def reset(self):
        pass

    def get_log_list(self):
        return self.log_list


    def print_log(self):
        print('--------------------------')
        for item in self.log_list:
            print(item.log_time, item.title, item.content)
        print('--------------------------')

    def get_json(self):
        res = []
        for item in self.log_list:
            temp = {
                "date":item.get_date(),
                "time":item.get_time(),
                "title":item.get_title(),
                "content":item.get_content()
            }
            res.append(temp)
        return json.dumps(res)
        

path_temp = os.path.join(os.path.dirname(__file__),"../../data/tmp/xlog.bin") 
xlogger = XLogger(path_temp)
xlogger.reset()

        

    
    