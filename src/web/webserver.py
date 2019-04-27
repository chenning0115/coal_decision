import tornado.ioloop
import tornado.web
from tornado.web import StaticFileHandler

import os
import sys
import math
import json, threading,time
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
import webconf
from launch import get_cur_time, launch, get_gas_analysis_obj
from launch import fmd, index2time
from monitor.monitor_define import get_monitor_ids_by_type,MONITOR_DEFINE
from decision.gas_analysis import SuggenstionType
import aggregate_analysis
from coal_case.caseobj import find_one_obj
from coal_case.search import Search
from suggestion_function import suggest_electronic
from xlog.xlog import xlogger,LogType

searcher = Search()

class RawDetailHanlder(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_rawdetail)

class GetGasMonitorDataHandler(tornado.web.RequestHandler):
    def get(self):
        update, cur_index, cur_time = get_cur_time()
        last_window = 10
        next_window = 5
        res = {
                'cur_date':cur_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        if update:
            gas_mids = get_monitor_ids_by_type(typestr='CH4')
            res['mids'] = gas_mids
            indexes = [cur_index-i for i in range(last_window,0,-1)] + [cur_index] + [cur_index+i+1 for i in range(next_window)]
            dates = [d.strftime("%Y-%m-%d %H:%M:%S") for d in index2time(indexes)]
            res['dates'] = dates
            for mid in gas_mids:
                mid_data = fmd.get_monitor_data_by_id_and_time(mid, cur_index, last_window, next_window)
                res[mid] = [[i,j] for i,j in zip(dates,mid_data)]
                res['last_%s' % mid] = [[i,j] for i,j in zip(dates[:last_window+1],mid_data[:last_window+1])]
                res['next_%s' % mid] = [[i,j] for i,j in zip(dates[last_window:],mid_data[last_window:])]
            ss =  json.dumps(res)
            self.write(ss)
        else:
            self.write({})
    
    
class GetGasAnalysisEventHandler(tornado.web.RequestHandler):
    def get(self):
        res = aggregate_analysis.aggregate_event(get_gas_analysis_obj())
        # print('get_event=',res)
        self.write(json.dumps(res))


class GetGasAnalysisSuggestionHandler(tornado.web.RequestHandler):
    def get(self):
        res = aggregate_analysis.aggregate_suggestion(get_gas_analysis_obj())
        # print('get_event=',res)
        self.write(json.dumps(res))
      
class SuggestEventHandler(tornado.web.RequestHandler):
    def get(self):
        update, cur_index, cur_time = get_cur_time()
        res = {}
        sug_id = self.get_argument('sug_id', None)
        gas_analysis_obj = get_gas_analysis_obj()
        sug_obj = gas_analysis_obj.suggestion_analysis_obj.get_suggestion_info(sug_id)
        if sug_obj.suggenstion_type == SuggenstionType.SUGGESTION_SIMPLE_ACTION:
            if sug_obj.execute_func is not None:
                sug_obj.execute(gas_analysis_obj,xlogger,cur_time)
        elif sug_obj.suggenstion_type in [SuggenstionType.SUGGESTION_ORGANIZE,
                            SuggenstionType.SUGGESTION_ELECTONIC,
                            SuggenstionType.SUGGESTION_AIR]:
            print(sug_obj.suggestion_id)
            res['operate'] = 'redirect'
            res['url'] = '/%s' % sug_obj.suggenstion_type
        self.write(json.dumps(res))
            

class ElectronicHandler(tornado.web.RequestHandler):
    def get(self):
        gas_analysis_obj = get_gas_analysis_obj()
        r1 = aggregate_analysis.aggregate_event(gas_analysis_obj)
        r2 = suggest_electronic(gas_analysis_obj)
        
        return self.render(webconf.path_template_electronic,r1=r1, r2=r2)

class ElecSureHandler(tornado.web.RequestHandler):
    def get(self):
        update, cur_index, cur_time = get_cur_time()
        xlogger.append_log(cur_time, "提交断电请求","已经向电力控制系统提交断电请求...",log_type=LogType.LOGTYPE_ACTION)
        time.sleep(2)
        res = {
            "status":"ok",
            "info":"已经转发控制系统，确认停止该位置电力供应。",
        }
        # 记录Log
        update, cur_index, cur_time = get_cur_time()
        xlogger.append_log(cur_time, "确认断电成功","获取电力控制系统断电成功信息...",log_type=LogType.LOGTYPE_ACTION)
        self.write(json.dumps(res))

class EscapeHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_escape)

class FindOneCaseHandler(tornado.web.RequestHandler):
    def get(self):
        _id = self.get_argument('_id', "5c8fa0fb230b945f6e4de092")
        _query = self.get_argument('_query',"")
        obj = find_one_obj(_id)
        obj.query = _query
        return self.render(webconf.path_template_formatdetail, mydoc = obj.format_mydoc(), obj=obj)


class CaseSearchHandler(tornado.web.RequestHandler):
    def get(self):
        #获取关键词
        query = self.get_argument('q', "瓦斯突出")
        #获取当前时间和监测数据
        update, cur_index, cur_time = get_cur_time()
        data = fmd.get_cur_data(index=cur_index)
        id2data= {}
        for mid,item in data.items():
            id2data[mid] = {
                'define':MONITOR_DEFINE[mid],
                'val':item[0]
            }
        target_case_monitor = {
            "CH4HL":[-1,1],
            "CO2HL":[-1,1],
            "COHL":[-1,1],
            "QTJCHS":[-1,1]
        }
        monitor_data = []
        for mid,dd in id2data.items():
            monitor_data.append([mid,dd['define']['POS']['TEXT'],dd['define']['TYPE'],dd['val']])
            if dd['define']['TYPE']=="CH4":
                if target_case_monitor['CH4HL'][0] < dd['val']:
                    target_case_monitor['CH4HL'][0] = dd['val']
            elif dd['define']['TYPE']=="CO":
                if target_case_monitor['COHL'][0] < dd['val']:
                    target_case_monitor['COHL'][0] = dd['val']
            elif dd['define']['TYPE']=="CO2":
                if target_case_monitor['CO2HL'][0] < dd['val']:
                    target_case_monitor['CO2HL'][0] = dd['val']
            else:
                pass
        
        obj_list = searcher.search(query, target_case_monitor)

        #just for extract
        # path = '../../data/extract/%s.txt' % (query)
        # if not os.path.exists(path):
        #     with open(path ,"w") as fout:
        #         for obj in obj_list:
        #             fout.write('%s\n' % (obj.sid))
        #         fout.flush()
        #     print('create file done.')

        return self.render(webconf.path_template_case_search, objs = obj_list,
                 monitor_data=monitor_data, timestr=str(cur_time), query=str(query))

class TimelineHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_timeline)

class TimelineDataHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(xlogger.get_json())
        


# settings and URL Mapping

settings = {
"static_path": os.path.join(os.path.dirname(__file__), "static") 
}



current_path = os.path.dirname(__file__)
application = tornado.web.Application([
        (r"/home",RawDetailHanlder),
        (r"/get_gas_monitor_data",GetGasMonitorDataHandler),
        (r"/get_gas_analysis_event",GetGasAnalysisEventHandler),
        (r"/get_gas_suggestion", GetGasAnalysisSuggestionHandler),
        (r"/suggest_event",SuggestEventHandler),
        (r"/suggestion_electronic",ElectronicHandler),
        (r"/suggestion_escape",EscapeHandler),
        (r"/find_one", FindOneCaseHandler),
        (r"/case_search", CaseSearchHandler),
        (r"/elec_sure", ElecSureHandler),
        (r"/timeline", TimelineHandler),
        (r"/timeline_data", TimelineDataHandler),
        (r'^/icon/(.*)$', StaticFileHandler, {"path":os.path.join(current_path, "static/icon")}),
        
    ],**settings)



 # run...
if __name__ == "__main__":
    launch()
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()

