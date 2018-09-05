#!/usr/local/python35/bin/python3.5
#-*- coding:utf8 -*-

import paramiko
import logging

class DOSSH(object):

  def __init__(self,ARGS):
    self.ARGS = ARGS

  @staticmethod
  def INITFUNC(ARGS):
    HAND = DOSSH(ARGS)
    if HAND.SSH():
      return True
    else:
      return False

  def SSH(self):
    try:
      COMMAND = "wget http://ali-hangzhou.oss-cn-hangzhou.aliyuncs.com/transfer.sh;bash transfer.sh %s %s %s"\
                %(self.ARGS['model'],self.ARGS['cfg'],self.ARGS['sys'])
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(str(self.ARGS["ip"]),int(self.ARGS["port"]),str(self.ARGS["username"]),str(self.ARGS["passwd"]))
      stdin, stdout, stderr = ssh.exec_command(COMMAND,timeout=20)
      logging.info(stdout.read().decode('utf-8').encode('utf-8'))
      ssh.close()
      return True
    except Exception as e:
      logging.info(e)
      return False
