import tornado.ioloop
import tornado.web

import os
import sys
import math
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
import webconf

class RawDetailHanlder(tornado.web.RequestHandler):
    def get(self):
        return self.render(webconf.path_template_rawdetail)



# settings and URL Mapping

settings = {
"static_path": os.path.join(os.path.dirname(__file__), "static") 
}

application = tornado.web.Application([
        (r"/home",RawDetailHanlder),
    ],**settings)



 # run...
if __name__ == "__main__":
    
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()

