import tornado.ioloop
import tornado.web

import os
import sys
import math
import json, threading
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
import webconf
from launch import get_cur_time, launch, get_gas_analysis_obj
from launch import fmd, index2time
from monitor.monitor_define import get_monitor_ids_by_type
from decision.gas_analysis import SuggenstionType
import aggregate_analysis
from coal_case.caseobj import find_one_obj
from coal_case.search import Search

searcher = Search()

class RawDetailHanlder(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_rawdetail)

class GetGasMonitorDataHandler(tornado.web.RequestHandler):
    def get(self):
        update, cur_index, cur_time = get_cur_time()
        last_window = 30
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
                res[mid] = mid_data
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
        res = {}
        sug_id = self.get_argument('sug_id', None)
        gas_analysis_obj = get_gas_analysis_obj()
        sug_obj = gas_analysis_obj.suggestion_analysis_obj.get_suggestion_info(sug_id)
        if sug_obj.suggenstion_type == SuggenstionType.SUGGESTION_SIMPLE_ACTION:
            if sug_obj.execute_func is not None:
                sug_obj.execute(gas_analysis_obj)
        elif sug_obj.suggenstion_type in [SuggenstionType.SUGGESTION_ORGANIZE,
                            SuggenstionType.SUGGESTION_ELECTONIC,
                            SuggenstionType.SUGGESTION_AIR]:
            print(sug_obj.suggestion_id)
            res['operate'] = 'redirect'
            res['url'] = '/%s' % sug_obj.suggenstion_type
        self.write(json.dumps(res))
            

class ElectronicHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_electronic)

class EscapeHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_escape)

class FindOneCaseHandler(tornado.web.RequestHandler):
    def get(self):
        _id = self.get_argument('_id', "5c8fa0fb230b945f6e4de092")
        obj = find_one_obj(_id)
        
        return self.render(webconf.path_template_formatdetail, mydoc = obj.format_mydoc(), obj=obj)


class CaseSearchHandler(tornado.web.RequestHandler):
    def get(self):
        query = self.get_argument('q', "瓦斯突出")
        obj_list = searcher.search(query)
        return self.render(webconf.path_template_case_search, objs = obj_list)
# settings and URL Mapping

settings = {
"static_path": os.path.join(os.path.dirname(__file__), "static") 
}

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
    ],**settings)



 # run...
if __name__ == "__main__":
    launch()
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()

