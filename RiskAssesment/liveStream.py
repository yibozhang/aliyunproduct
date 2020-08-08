# -*- coding:utf-8 -*-
import threading
import asyncio
import time
import urllib3 
import json
from aliyun.log import *
from aliyun.log.util import base64_encodestring
from random import randint

# variable

flag=0
stime=int(time.time()) - 43200
etime=int(time.time())
cdnsky=""
http = urllib3.PoolManager()
allStrategyID={}
strategyResult=[]


# corotine 

@asyncio.coroutine
def hello(host):

 global flag
 if flag == 100:
  time.sleep(1)
  flag=0
 flag += 1
 yield printd(host) 
 queryResult(allStrategyID)


# get cdnskys liveStreamlimit instance id 

def printd(host):
 url="http://cdnskyeye.alibaba-inc.com/api/lualib/diagnose.diagnose/start_diagnose?strategy_id=247&author=%E9%9F%A9%E7%AC%A0&LiveDomain=" + host + f"&StartTime={stime}&EndTime={etime}"
 resp = http.request('GET',url)
 try:
  if resp.data: 
   msg = json.loads(resp.data.decode())['content']['instance_id']
  allStrategyID[host] = msg
 except Exception as e:
  print(e)


# query assert result

def queryResult(id):
 print("[DebugLength]->",len(id))
 
 if not id:
  exit()
 while True:
  for key in list(id.keys()):
   url = f"http://cdnskyeye.alibaba-inc.com/api/lualib/diagnose.diagnose/diagnose_instance?instance_id={id[key]}"
   resp = http.request('GET',url)
   if resp.data:
    msg = json.loads(resp.data.decode())
    if msg:
     strategyResult.append((msg['content'][0]['result'][0]))
     id.pop(key)
  if not id:
   logTail(strategyResult)
   break 

# wirte sls log

def logTail(result):
 print("[Debug LogTail]->",len(result))
 endpoint = "cn-zhangjiakou.log.aliyuncs.com"
 accessKeyId = ""
 accessKey = ""
 logstore = ""
 project = ""
 client = LogClient(endpoint, accessKeyId, accessKey)
 topic = '直播业务'
 source = ''
 logitemList = []
 for i in range(len(result)):
  contents = [
        ('product_name', 'livestream'),
        ('ali_uid',json.loads(result[i]['result'])['uid']),
        ('start_time', str(stime)),
        ('end_time', str(etime)),
        ('domain',json.loads(result[i]['result'])['domain']),
        ('status',json.loads(result[i]['result'])['status']),
        ('solution',json.loads(result[i]['result'])['solution']),
        ('officialResponse',json.loads(result[i]['result'])['officialResponse']),
        ('desc',json.loads(result[i]['result'])['desc']),
        ('detail',json.loads(result[i]['result'])['detail'])
  ]
  logItem = LogItem()
  logItem.set_time(int(time.time()))
  logItem.set_contents(contents)
  logitemList.append(logItem)
  if len(logitemList) >= 1000:
   request = PutLogsRequest(project, logstore, topic, source, logitemList)
   response = client.put_logs(request)
   response.log_print()
   logitemList = []
 request = PutLogsRequest(project, logstore, topic, source, logitemList)
 response = client.put_logs(request)
 response.log_print()

files = open('live_domain.lst','r')
loop = asyncio.get_event_loop()
tasks = [hello(i.strip('\n')) for i in files.readlines()]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
