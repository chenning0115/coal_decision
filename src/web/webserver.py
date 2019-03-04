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

import aggregate_analysis

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
        print('get_event=',res)
        self.write(json.dumps(res))

            
            



# settings and URL Mapping

settings = {
"static_path": os.path.join(os.path.dirname(__file__), "static") 
}

application = tornado.web.Application([
        (r"/home",RawDetailHanlder),
        (r"/get_gas_monitor_data",GetGasMonitorDataHandler),
        (r"/get_gas_analysis_event",GetGasAnalysisEventHandler),
    ],**settings)



 # run...
if __name__ == "__main__":
    launch()
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()

