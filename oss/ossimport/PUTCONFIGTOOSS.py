#!/usr/bin/env python
import oss2

class PUTCONFIGTOOSS(object):

  def __init__(self,DEST,STORESIZE):
    self.AK = ''
    self.SK = ''
    self.ENDPOINT = 'http://oss-cn-hangzhou.aliyuncs.com'
    self.BUCKET = 'ali-hangzhou'
    self.DEST = DEST
    self.STORESIZE = STORESIZE


  def INITIAL(self):
    try:

      AUTH = oss2.Auth(self.AK,self.SK)
      BUCKETS = oss2.Bucket(AUTH, self.ENDPOINT,self.BUCKET)
      SYSOBJS = '{0}/sys.properties'.format(self.DEST)

      if self.STORESIZE == "less-than-30":
        OBJECTS = '{0}/local_job.cfg'.format(self.DEST)
      else:
        OBJECTS = '{0}/{1}.cfg'.format(self.DEST,self.DEST)

      with open('/tmp/{0}.cfg'.format(self.DEST), 'rb') as FILEOBJ:
        OSSRESP = BUCKETS.put_object(OBJECTS, FILEOBJ)

      with open('/tmp/{0}.properties'.format(self.DEST), 'rb') as SYSOBJ:
        SYSRESP = BUCKETS.put_object(SYSOBJS, SYSOBJ)

      CFGDOWN = 'http://{0}.oss-cn-hangzhou.aliyuncs.com/{1}'.format(self.BUCKET,OBJECTS)
      SYSDOWN = 'http://{0}.oss-cn-hangzhou.aliyuncs.com/{1}'.format(self.BUCKET,SYSOBJS)

      return CFGDOWN,SYSDOWN

    except Exception:
      print(e)
      return e
