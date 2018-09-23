#-*- coding:utf8 -*-
from optparse import OptionParser
import collections
import oss2
import sys
import re

class MainFunction():

  def __init__(self,options):

    self.args = collections.OrderedDict()
    self.args["ak"] = options.ak
    self.args["sk"] = options.sk
    self.args["ed"] = options.ed
    self.args["bk"] = options.bk
    self.args["cdn"] = options.cdn
    self.args["types"] = options.types
    self.args["meth"] = options.meth
    self.left = '\033[1;31;40m'
    self.right = '\033[0m'

  # check input parse

  def CheckParse(self):

    try:

      for keys in self.args:
        if self.args[keys] == None:
          self.ConsoleLog(0)
          return False

      if not (self.args['ed'].startswith("http://") or self.args['ed'].startswith("https://")):
       self.args['ed'] = "http://"+self.args['ed']

      if not (self.args['cdn'].startswith("http://") or self.args['cdn'].startswith("https://")):
        self.ConsoleLog(1)
        return False

      if not re.match("(GET|POST|PUT|HEAD|DELETE|ORIGIN)",self.args['meth']):
        self.ConsoleLog(7)
        return False

      if not re.match("multi|single",self.args['types']):
        self.ConsoleLog(2)
        return False
    
    except Exception as e:
      self.ConsoleLog(e)

    return True

  # valid cors config 

  def ValidConf(self,origins,methods,headers,expose,flag=True):

    try:

      if not (re.match(self.args['cdn'],origins) or origins=="*"):
        flag=False
        self.ConsoleLog(3)
 
      if not (re.match(str(methods.split(",")),self.args['meth']) or methods=="*"):
        flag=False
        self.ConsoleLog(4)

      if self.args['types'] == "multi":
        if not (re.match("(etag|Etag|\*| )",expose)):
          flag=False
          self.ConsoleLog(6)

      if headers == None:
        flag=False
        self.ConsoleLog(5)


    except Exception as e:
      self.ConsoleLog(e) 

    return flag

  # get oss cors config

  def GetCors(self):

    try:
      auth = oss2.Auth(self.args['ak'], self.args['sk'])
      bucket = oss2.Bucket(auth, self.args['ed'], self.args['bk'])
      cors = bucket.get_bucket_cors()
    except oss2.exceptions.ServerError as e:
      self.ConsoleLog(e)
    except oss2.exceptions.NoSuchCors as e:
      self.ConsoleLog(e)
    except oss2.exceptions.NoSuchBucket as e:
      self.ConsoleLog(e)
    except oss2.exceptions.AccessDenied as e:
      self.ConsoleLog(e)
    else:
      for rule in cors.rules:
        if (self.ValidConf(",".join(rule.allowed_origins),",".join(rule.allowed_methods),
        ",".join(rule.allowed_headers),",".join(rule.expose_headers))):
          self.ConsoleLog(8)

  # output error log

  def ConsoleLog(self,level):

    if level == 0:
      print('{0}[ERROR]{1}All parameters cannot be empty'.format(self.left,self.right))
      
    if level == 1:
      print('{0}[ERROR]{1}<-s> CDN domain must be http|https start'.format(self.left,self.right))

    if level == 2:
      print('{0}[ERROR]{1}<-t> Must be multi|single'.format(self.left,self.right))
    
    if level == 3:
      print('{0}[CheckResult]{1}OSS Access-Control-Allow-Origin Config Error {2}, You can fill in * or http://domain'.format(self.left,self.right,self.args['cdn']))

    if level == 4:
      print('{0}[CheckResult]{1}OSS Access-Control-Allow-Methods Config Error{2}, You can fill in * or methods'.format(self.left,self.right,self.args['meth']))

    if level == 5:
      print('{0}[CheckResult]{1}Access-Control-Allow-Headers OSS Config Error, You can fill in * or headers'.format(self.left,self.right))

    if level == 6:
      print('{0}[CheckResult]{1}Multipart operate must set expose <etag|Etag|*>'.format(self.left,self.right))

    if level == 7:
      print('{0}[ERROR]{1}<-m> Must be <GET|POST|PUT|HEAD|DELETE|ORIGIN> ,multiple method please "," split'.format(self.left,self.right))

    if level == 8:
      sys.exit("[CheckResult]OSS CORS Config Alright OK")

    if not isinstance(level,int):
      print(level)

#      expr1 = lambda x:x if x.startswith("http://") or x.startswith("https://") else "https://"+x
#      expr2 = lambda y:y if y.startswith("http://") or y.startswith("https://") else "https://"+y

if __name__ == "__main__":

  parser = OptionParser()
  parser.add_option("-i",dest="ak",help="<Accesskey>")
  parser.add_option("-k",dest="sk",help="<AccessKeySecrety>")
  parser.add_option("-e",dest="ed",help="dest oss <endpoint>")
  parser.add_option("-b",dest="bk",help="dest oss <bucket>")
  parser.add_option("-s",dest="cdn",help="cors allow <domain>")
  parser.add_option("-m",dest="meth",help="cors http method <GET,POST,PUT,HEADER>")
  parser.add_option("-t",dest="types",help="cors file type multiparts operate or single operate<multi,single>")
  (options, args) = parser.parse_args()
  handler = MainFunction(options)

  if handler.CheckParse():
    handler.GetCors()

