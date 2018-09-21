from optparse import OptionParser
import urllib,urllib2
import datetime
import base64
import hmac
import sha
import os
import sys
import time


class Main():
  
  # Initial input parse

  def __init__(self,options):

    self.ak = options.ak
    self.sk = options.sk
    self.ed = options.ed
    self.bk = options.bk
    self.fi = options.fi
    self.oj = options.objects
    self.types = "application/x-www-form-urlencoded"    
    self.url = 'http://{0}.{1}/{2}'.format(self.bk,self.ed,self.oj)

  # Check client input parse

  def CheckParse(self):

    if (self.ak and self.sk and self.ed and self.bk and self.oj and self.fi) != None:
      if str(self.ak and self.sk and self.ed and self.bk and self.oj and self.fi):
        return True
    else:
      return False

  # GET local GMT time

  def GetGMT(self):
  
    SRM = datetime.datetime.utcnow()
    GMT = SRM.strftime('%a, %d %b %Y %H:%M:%S GMT')
    self.stamp = int(time.mktime(time.strptime(SRM.strftime('%a %b %d %H:%M:%S %Y'))))+32400
    
    return GMT

  # GET Signature

  def GetSignature(self):

    mac = hmac.new("{0}".format(self.sk),"PUT\n\n{0}\n{1}\nx-oss-expires:{4}\n/{2}/{3}".format(self.types,self.GetGMT(),self.bk,self.oj,self.stamp), sha)
    Signature = base64.b64encode(mac.digest())
   
    return Signature

  # PutObject

  def PutObject(self):
   
    try: 
      with open(self.fi) as fd:
        files = fd.read()
    except Exception:
      sys.exit('\033[1;31;40m[error:]\033[0mFail to read localfile')
  
    try:
      request = urllib2.Request(self.url, files)
    except Exception:
      sys.exit('\033[1;31;40m[error:]\033[0mraise AttributeError, attr')

    try:
     request.add_header('Host','ali-beijing.oss-cn-beijing.aliyuncs.com')
     request.add_header('Date','{0}'.format(self.GetGMT()))
     request.add_header('x-oss-expires','{0}'.format(self.stamp))
     request.add_header('Authorization','OSS {0}:{1}'.format(self.ak,self.GetSignature()))
     request.get_method = lambda:'PUT'
     response = urllib2.urlopen(request,timeout=10)
     sys.exit("\n%s"%response.headers)
    except Exception,e:
      sys.exit('\n\033[1;31;40m[error:]\033[0m%s'%e)
 

if __name__ == "__main__":

  parser = OptionParser()
  parser.add_option("-i",dest="ak",help="Must fill in Accesskey")
  parser.add_option("-k",dest="sk",help="Must fill in AccessKeySecrety")
  parser.add_option("-e",dest="ed",help="Must fill in endpoint")
  parser.add_option("-b",dest="bk",help="Must fill in bucket")
  parser.add_option("-o",dest="objects",help="File name uploaded to oss")
  parser.add_option("-f",dest="fi",help="Must fill localfile path")

  (options, args) = parser.parse_args()
  handler = Main(options)

  if handler.CheckParse():
    handler.PutObject()
  else:
    sys.exit('\033[1;31;40m[error:]\033[0mCheck your parse not null')
