#!/usr/bin/env python
#-*- coding:utf8 -*_
#Describe: Reciver Input Args from User
#Updata：2018-05-01
#Author：hanli.zyb

import collections
import logging
import time
from PUTCONFIGTOOSS import *

class PRODUCECONFIG(object):

 def __init__(self,ARGS):

   self.INPUT = ARGS
   self.JOBS = collections.OrderedDict()
   self.SYS = collections.OrderedDict()
   self.INTODICT = collections.OrderedDict()

 # 初始化，静态实例化对象
 @staticmethod
 def INITFUNC(ARGS):
   RESULT = PRODUCECONFIG(ARGS)
   if RESULT.READCONFIG():
     if RESULT.CHECKINPUTARGS():
       if RESULT.JOBANDSYS():
         HAND = PUTCONFIGTOOSS(ARGS['destBucket'],ARGS['storesize'])
         DOWN = HAND.INITIAL()
         return DOWN
       else:
         return False
     else:
       return False
   else:
     return False

 # 读取原生 job.cfg sys.properties 文件存入字典内
 def READCONFIG(self):

   try:
     with open('job.cfg','r') as HF:
       JOBCFG = HF.read().split('\n')
       while '' in JOBCFG:
         JOBCFG.remove('') 
       for KEY in JOBCFG: 
         VALUE = KEY.split('=')
         self.JOBS[VALUE[0]] = VALUE[1]
  
     with open('sys.properties','r') as HP:
       SYSPRO = HP.read().split('\n')
       while '' in SYSPRO:
         SYSPRO.remove('')
       for PRO in SYSPRO:
         PROS = PRO.split('=')
         self.SYS[PROS[0]] = PROS[1]
     return True

   except Exception:
     logging.info(e)
     return False

 # 检查 web 输入参数是否为空
 def CHECKINPUTARGS(self):
   logging.info(self.INPUT)
   for KEY in self.INPUT:
     VALUE = self.INPUT[KEY]

     if KEY == "srcPrefix" or KEY == "destPrefix":
       self.INTODICT[KEY] = VALUE

     else:
       if VALUE != "":
         self.INTODICT[KEY] = VALUE
       else:
         return False

   return True

 # 根据 ECS 选型后调用更改配置属性
 def JOBANDSYS(self):

   if self.INTODICT['ecsnum'] > "1" and self.INTODICT['storesize'] == "more-than-30":

     if self.INTODICT['ecs'] == "LD":
       self.CHANGEARGS()
     elif self.INTODICT['ecs'] == "MD":
       self.CHANGEARGS(60,"4096m")
     elif self.INTODICT['ecs'] == "HD":
       self.CHANGEARGS(80,"16384m")
     elif self.INTODICT['ecs'] == "SD":
       self.CHANGEARGS(120,"65535m")
     elif self.INTODICT['ecs'] == "TD":
       self.CHANGEARGS(180,"131072m")
     else:
       logging.info('ecs 型号错误') 
       return False
     self.OUTPUTCONFIG()

   else:
     self.CHANGEARGS()
     self.OUTPUTCONFIG()

   return True

 # 将job sys 的属性改写为用户前端提交的参数
 def CHANGEARGS(self,workerTaskThreadNum=60,javaHeapMaxSize="2048m"):

   self.SYS['workerTaskThreadNum'] = workerTaskThreadNum
   self.SYS['javaHeapMaxSize'] = javaHeapMaxSize
   
   if self.INTODICT['ecsnum'] == "1":
     self.JOBS['taskObjectCountLimit'] = 10000
     self.JOBS['jobName'] = 'local_test'
   else:
     self.JOBS['jobName'] = str(int(time.time()))+"-"+self.INTODICT['destBucket']
     self.JOBS['taskObjectCountLimit'] = int(int(self.INTODICT['filenum'])/int(workerTaskThreadNum*int(self.INTODICT['ecsnum'])))+1

   for KEY in self.INTODICT:
     if KEY in self.JOBS:
       self.JOBS[KEY] = self.INTODICT[KEY]

 # 写入配置文件
 def OUTPUTCONFIG(self):

   try:  
     SYSNAME = self.INTODICT['destBucket'] + ".properties"

     with open('/tmp/%s.cfg'%self.INTODICT['destBucket'],'w') as FO:
       for KEY1 in self.JOBS:
         FO.write('{0}={1}\n'.format(KEY1,self.JOBS[KEY1]))
     
     with open('/tmp/%s'%SYSNAME,'w') as SO:
       for KEY2 in self.SYS:
         SO.write('{0}={1}\n'.format(KEY2,self.SYS[KEY2]))

   except Exception:
     logging.info(e)
