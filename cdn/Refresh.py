#!/usr/bin/env python
#coding=utf-8
# __author__ = 'hanli.zyb'

'''Check Package'''

try:
 import os, sys, getopt, time, json
 from aliyunsdkcore.client import AcsClient
 from aliyunsdkcore.acs_exception.exceptions import ClientException
 from aliyunsdkcore.acs_exception.exceptions import ServerException
 from aliyunsdkcdn.request.v20180510.RefreshObjectCachesRequest import RefreshObjectCachesRequest
 from aliyunsdkcdn.request.v20180510.PushObjectCacheRequest import PushObjectCacheRequest
 from aliyunsdkcdn.request.v20180510.DescribeRefreshTasksRequest import DescribeRefreshTasksRequest
 from aliyunsdkcdn.request.v20180510.DescribeRefreshQuotaRequest import DescribeRefreshQuotaRequest
except:
 sys.exit("[Error] Please pip install aliyun-python-sdk-cdn and aliyun-java-sdk-core ，please install now......")

class Refresh(object):

  '''init func'''

  def __init__(self):

   self.lists = []
   self.param = {}

  '''
  描述：调度的主函数
  resP：检测入参结果，如果类型不是 bool 说明有报错
  '''

  def main(self,argv):
    if len(argv) < 1 :
      sys.exit("\nusage: " + sys.argv[0] + " -h ")
    try:
      opts,args = getopt.getopt(argv,"hi:k:n:r:t:")
    except Exception as e :
      sys.exit("\nusage: " + sys.argv[0] + " -h ")
  
    for opt,arg in opts:
      if opt == '-h':
        self.helps()
        sys.exit()
      elif opt == '-i':
        self.param['-i'] = arg
      elif opt == '-k':
        self.param['-k'] = arg
      elif opt == '-r':
        self.param['-r'] = arg
      elif opt == '-t':
        self.param['-t'] = arg
      elif opt == '-n':
        self.param['-n'] = int(arg)
      else:
        sys.exit("\nusage: " + sys.argv[0] + " -h ")
  
    resP = self.doCheck(self.param)
    if not isinstance(resP,bool): sys.exit(resP)
    
    try:
      client = AcsClient(self.param['-i'], self.param['-k'], 'cn-hangzhou')
    except NameError:
      sys.exit("[Error]: SDK module not detected")

    for g in self.doProd(self.param):
      self.lists = []
      self.doRefresh(''.join(g),self.param['-t'],client)

  '''
  描述：检测入参数
  '''
  def doCheck(self,param):
    files = os.path.abspath(param['-r'])

    if not files : return "[Error]: filename Not Found"
    if not param['-t'] in ("push","clear"): return "[Error]: taskType Error"
    if not param.has_key('-n'):
      self.param['-n'] = 50
    elif not (abs(param['-n']) <= 100 and isinstance(param['-n'],int)):
      return "[Error]: nums Type or Value Error"
    return True
  
  '''
  描述：生成器切分文件，对每行文件进行处理 '\n'
  gop：每次读取 URL 数量
  '''
  def doProd(self,params):
    gop = params['-n']
    mins = 1
    maxs = gop

    with open(params['-r'], "r") as f:
      for line in f.readlines():
        if mins != maxs:
         line = line.strip("\n") + "\n"
        else:
         line = line.strip("\n")
        self.lists.append(line)
        if mins >= maxs:
         yield self.lists
         mins = maxs
         maxs = gop + maxs -1
        else:
         mins += 1
      if len(self.lists) > 0: yield self.lists
       
  '''
  描述：刷新/预热任务
  '''
  def doRefresh(self,lists,types,client):

     if types == 'clear':
       taskID = 'RefreshTaskId'
       request = RefreshObjectCachesRequest()
     elif types == 'push':
       taskID = 'PushTaskId'
       request = PushObjectCacheRequest()

     taskreq = DescribeRefreshTasksRequest()
     request.set_accept_format('json')
     request.set_ObjectPath(lists)
     response = json.loads(client.do_action_with_exception(request))
     print(response)
    
     while True:
      count = 0
      taskreq.set_accept_format('json')
      taskreq.set_TaskId(int(response[taskID]))
      taskresp = json.loads(client.do_action_with_exception(taskreq))
      print("[" + response[taskID] + "]" + "is doing... ...")
      for t in taskresp['Tasks']['CDNTask']:
       if t['Status'] != 'Complete':
        count += 1
      if count == 0:
       break
      else:
       continue
      time.sleep(1)

  '''
  描述：帮助信息
  '''
  def helps(self):
    print("\nscript options explain: \
            \n\t -i <AccessKey>       访问阿里云凭证，访问控制台上可以获得； \
            \n\t -k <AccessKeySecret> 访问阿里云秘钥，访问控制台上可以获得； \
            \n\t -r <filename>        文件名称，每行一条 URL，有特殊字符先做 URLencode，以 http/https 开头； \
            \n\t -t <taskType>        任务类型 clear 刷新，push 预热； \
            \n\t -n [nums,[..100]]    可选项，每次操作文件数量，做多 100 条；")

#TODO 入口

if __name__ == '__main__':
  fun = Refresh()
  fun.main(sys.argv[1:])
