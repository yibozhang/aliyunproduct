#-*- coding:utf-8 -*-
# Adult: hanli.zyb@alibaba-inc.com
# Describe: reciver input args from webjs
# Update: 2018-03-23

from tornado.options import define,options
from PRODUCECONFIG import *
from DOSSH import *
import collections
import tornado.ioloop
import tornado.web
import tornado.httpserver
import logging
import oss2
import os

define( "port", default=1989, help="Run server on a specific port", type=int )
settings = { "static_path": os.path.join(os.path.dirname(__file__), "static"), }

class MainFunction(tornado.web.RequestHandler):

  def initialize(self):
    self.rip = self.request.remote_ip

  def get(self):
    logging.info(self.rip+"|"+self.request.uri+"|"+self.request.method)
    self.render("portal.html",title=title)

class OssBase(tornado.web.RequestHandler):

  def initialize(self):
    self.rip = self.request.remote_ip

  def post(self):
    logging.info(self.rip+"|"+self.request.uri+"|"+self.request.method)

    try:
      store = self.get_argument("store")
      style = self.get_argument("style")
      self.write("model={0}&size={1}".format(style,store))
    except Exception as e:
      logging.info(e)

class GetConfig(tornado.web.RequestHandler):

   def initialize(self):
     self.rip = self.request.remote_ip

   def get(self):
     logging.info(self.rip+"|"+self.request.uri+"|"+self.request.method)
     model = self.get_argument("model",default="")
     size = self.get_argument("size",default="")
     self.render("configure.html",title=title,model=model,size=size)

class GetAll(tornado.web.RequestHandler):

   def judge(self,size,ecsnum):
     if ecsnum > "1" and size == "more":
       return "distribute"
     else:
       return "stand"
     
   def post(self):
     self.largs = collections.OrderedDict()
     style = self.get_argument("srcType")
     self.largs["destAccessKey"] = self.get_argument("destAccessKey",default="")
     self.largs["destSecretKey"] = self.get_argument("destSecretKey",default="")
     self.largs["destDomain"] = self.get_argument("destDomain",default="")
     self.largs["destBucket"] = self.get_argument("destBucket",default="")
     self.largs["destPrefix"] = self.get_argument("destPrefix",default="")
     self.largs["ecsnum"] = self.get_argument("ecsnum",default="")
     self.largs["filenum"] = self.get_argument("filenum",default="")
     self.largs["storesize"] = self.get_argument("storesize",default="")
     self.largs["ecs"] = self.get_argument("ecs",default="")

     if(style=="local"): 
       try:
         self.largs["srcType"] = style
         self.largs["srcPrefix"] = self.get_argument("srcPrefix")
         download = PRODUCECONFIG.INITFUNC(self.largs)
         result = self.judge(self.largs["storesize"],self.largs["ecsnum"])
         self.write("srcType={0}&cfg={1}&sys={2}".format(result,download[0],download[1]))
       except Exception as e:
         self.write("error") 
     elif(style == "http"):
       try:
         self.largs["srcType"] = style
         self.largs["httplistfilepath"] = self.get_argument("httplistfilepath",default="")
         download = PRODUCECONFIG.INITFUNC(self.largs)
         result = self.judge(self.largs["storesize"],self.largs["ecsnum"])
         self.write("srcType={0}&cfg={1}&sys={2}".format(result,download[0],download[1]))
       except Exception as e:
         self.write("error")
     else:
       try:
         self.largs["srcType"] = style
         self.largs["srcPrefix"] = self.get_argument("srcPrefix",default="")
         self.largs["srcAccessKey"] = self.get_argument("srcAccessKey",default="")
         self.largs["srcSecretKey"] = self.get_argument("srcSecretKey",default="")
         self.largs["srcDomain"] = self.get_argument("srcDomain",default="")
         self.largs["srcBucket"] = self.get_argument("srcBucket",default="")
         download = PRODUCECONFIG.INITFUNC(self.largs)
         result = self.judge(self.largs["storesize"],self.largs["ecsnum"])
         self.write("srcType={0}&cfg={1}&sys={2}".format(result,download[0],download[1]))
       except Exception as e:
         self.write("error")

class DeployIp(tornado.web.RequestHandler):

  def get(self):
    style = self.get_argument("srcType",default="")
    cfg = self.get_argument("cfg",default="")
    sys = self.get_argument("sys",default="")
    self.render("deploy.html",title=title,model=style,cfg=cfg,sys=sys)


class SSHIP(tornado.web.RequestHandler):
  def post(self):
    try:
      self.ssh = collections.OrderedDict()
      self.ssh['ip'] = self.get_argument('ip')
      self.ssh['port'] = self.get_argument('port')
      self.ssh['passwd'] = self.get_argument('passwd')
      self.ssh['username'] = self.get_argument('username')
      self.ssh['cfg'] = self.get_argument('cfg')
      self.ssh['sys'] = self.get_argument('sys')
      self.ssh['model'] = self.get_argument('model')
      if DOSSH.INITFUNC(self.ssh):
        self.write("successed")
      else:
        self.write("SSH Authorize Fail Please check You Input Mess!!!")
    except Exception:
      self.write("Get Your Input Mess has been error!!!")

application = tornado.web.Application([
 (r"/ossimport",MainFunction),
 (r"/ossbase",OssBase),
 (r"/getconfig",GetConfig),
 (r"/getall",GetAll),
 (r"/deployip",DeployIp),
 (r"/sship",SSHIP),
 (r"/",tornado.web.StaticFileHandler,dict(path=settings["static_path"])),
], **settings)

if __name__ == "__main__":

  title = "OSSimport 可视化迁移文件生成器 " 
  http_server = tornado.httpserver.HTTPServer(application)
  tornado.options.parse_command_line()
  application.listen(80)
  tornado.ioloop.IOLoop.instance().start()
