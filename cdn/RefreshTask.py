#!/usr/bin/python
#****************************************************************#
# ScriptName: RefreshTask.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2021-08-08 15:50
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2021-08-08 15:50
# Function:
#***************************************************************#
#!/usr/bin/env python3.5
# coding=utf-8
# __author__ = 'hanli.zyb'# __date__ = '2021-04-23'

'''Check Package'''

try:
    import os, re, sys, getopt, time, json, logging, subprocess
    from MysqlJDBC import *
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
    from aliyunsdkcdn.request.v20180510.RefreshObjectCachesRequest import RefreshObjectCachesRequest
    from aliyunsdkcdn.request.v20180510.PushObjectCacheRequest import PushObjectCacheRequest
    from aliyunsdkcdn.request.v20180510.DescribeRefreshTasksRequest import DescribeRefreshTasksRequest
    from aliyunsdkcdn.request.v20180510.DescribeRefreshQuotaRequest import DescribeRefreshQuotaRequest
except:
    sys.exit("[error] Please pip install aliyun-python-sdk-cdn and aliyun-python-sdk-core and logging，please install now......")
logging.basicConfig(level=logging.DEBUG, filename='/mnt/logs/RefreshAndPredload.log')

class Envariable(object):
    REGION = 'cn-hangzhou'
    retry = 0
    task_id = None
    task_ak = None
    task_sk = None
    task_file = None
    task_type = None
    task_area = None
    task_otype = None
    url_list = []
    task_list = []
    task_doing = []
    task_fail_id = []
    task_success_id = []

    def set_task_id(task_id):
        Envariable.task_id = task_id

    @staticmethod
    def get_task_id():
        return Envariable.task_id

    def set_task_file(task_file):
        Envariable.task_file = task_file

    @staticmethod
    def get_task_file():
        return Envariable.task_file

    def set_task_ak(task_ak):
        Envariable.task_ak = task_ak

    @staticmethod
    def get_task_ak():
        return Envariable.task_ak

    def set_task_sk(task_sk):
        Envariable.task_sk = task_sk

    @staticmethod
    def get_task_sk():
        return Envariable.task_sk

    def set_task_type(task_type):
        Envariable.task_type = task_type

    @staticmethod
    def get_task_type():
        return Envariable.task_type

    def set_task_area(task_area):
        Envariable.task_area = task_area

    @staticmethod
    def get_task_area():
        return Envariable.task_area

    def set_task_otype(task_otype):
        Envariable.task_otype = task_otype

    @staticmethod
    def get_task_otype():
        return Envariable.task_otype


class BaseCheck(object):

    def __init__(self):
        self.all_lines = 0

    # TODO Check Customer Quota
    def CheckQuota(self):
        logging.info("in ->>>>>>>>> CheckQuota")
        try:
            cal_lines = subprocess.getoutput("wc -l %s" % Envariable.get_task_file())
            self.all_lines = int(cal_lines.split()[0])
            client = AcsClient(Envariable.get_task_ak(), Envariable.get_task_sk(), Envariable.REGION)
            quotaResp = json.loads(client.do_action_with_exception(DescribeRefreshQuotaRequest()).decode('utf-8'))
        except Exception as e:
            MysqlJDBC.UPDATE_FAIL_STATUS("CheckQuota Failed", Envariable.get_task_id())
            logging.info('Error CheckQuota Func {0}'.format(e))
            return

        if Envariable.get_task_type():
            if Envariable.get_task_type() == 'push':
                if self.all_lines > int(quotaResp['PreloadRemain']):
                    MysqlJDBC.UPDATE_FAIL_STATUS("Insufficient preload quota",Envariable.get_task_id())
                    return
                return True
            if Envariable.get_task_type() == 'clear':
                if Envariable.get_task_otype() == 'File' and self.all_lines > int(quotaResp['UrlRemain']):
                    MysqlJDBC.UPDATE_FAIL_STATUS("Insufficient refresh quota",Envariable.get_task_id())
                    return
                elif Envariable.get_task_otype() == 'Directory' and self.all_lines > int(quotaResp['DirRemain']):
                    MysqlJDBC.UPDATE_FAIL_STATUS("Insufficient refresh quota",Envariable.get_task_id())
                    return
                else:
                    return True
        else:
            MysqlJDBC.UPDATE_FAIL_STATUS("Get task type Null", Envariable.get_task_id())
            logging.info("Error: Get task type Null")
            return

class doTask(object):

    # TODO URLEncoder
    def urlencode_pl(inputs_str):
        len_str = len(inputs_str)
        if str == "" or len_str <= 0:
            return ""
        index_j = 0
        index_i = 0
        result_end = ""
        for index_i in range(0, len_str):
            index_sb = index_i + 1
            chs = inputs_str[index_i:index_sb]
            if (chs >= 'A' and chs <= 'Z') or (chs >= 'a' and chs <= 'z') or (chs >= '0' and chs <= '9') or (
                    chs == ":") or (chs == "/"):
                if result_end == "":
                    result_end = chs
                else:
                    result_end += chs
            elif chs == ' ':
                result_end += '+'
            elif chs == '.' or chs == '-' or chs == '_' or chs == '*':
                result_end += chs
            else:
                result_end = '%s%%%02X' % (result_end, ord(chs))

        return result_end

    # TODO Split task URL
    @staticmethod
    def doProd():
        logging.info("in ->>>>>>>>> doProd")
        gop = 100
        mins = 1
        maxs = gop
        with open(Envariable.get_task_file(), "r") as f:
            for line in f.readlines():
                if mins != maxs:
                    line = line.strip("\n") + "\n"
                else:
                    line = line.strip("\n")
                line = line.strip()
                line = doTask.urlencode_pl(line) + "\n"
                Envariable.url_list.append(line)
                if mins >= maxs:
                    yield Envariable.url_list
                    mins = maxs
                    maxs = gop + maxs - 1
                else:
                    mins += 1
            if len(Envariable.url_list) > 0: yield Envariable.url_list

        f.close()

    def doRefresh(lists):
        try:
            logging.info("in ->>>>>>>>> doRefresh")
            client = AcsClient(Envariable.get_task_ak(), Envariable.get_task_sk(), Envariable.REGION)
            if Envariable.get_task_type() == 'clear':
                taskID = 'RefreshTaskId'
                request = RefreshObjectCachesRequest()
                if Envariable.get_task_otype():
                    request.set_ObjectType(Envariable.get_task_otype())
            elif Envariable.get_task_type() == 'push':
                taskID = 'PushTaskId'
                request = PushObjectCacheRequest()
                if Envariable.get_task_area():
                    request.set_Area(Envariable.get_task_area())
            else:
                MysqlJDBC.UPDATE_FAIL_STATUS("doRefresh get task type fail",Envariable.get_task_id())
                return
        except Exception as e:
            logging.info("Error: doRefresh Func {}".format(e))
            return

        try:
            request.set_accept_format('json')
            request.set_ObjectPath(lists)
            response = json.loads(client.do_action_with_exception(request).decode('utf-8'))
            Envariable.task_doing.append(response[taskID])
        except Exception as e:
            if re.match(r".*PreloadQueueFull", str(e)) and Envariable.retry == 0:
                print("PreloadQueueFull")
                time.sleep(5)
                Envariable.retry = 1
                doTask.doRefresh(lists)
            else:
                Envariable.task_fail_id.append(str(e))

class Check_Params(object):

    @staticmethod
    def Checking(params):
        logging.info("in ->>>>>>>>> Checking")
        try:
            for keys in params:
                if keys == 'RefreshOrPreheat' and params[keys]:
                    Envariable.set_task_type(params[keys])
                if keys == 'Area' and params[keys]:
                    Envariable.set_task_area(params[keys])
                if keys == 'ObjectType' and params[keys]:
                    Envariable.set_task_otype(params[keys])
                if keys == 'accessKeyId' and params[keys]:
                    Envariable.set_task_ak(params[keys])
                if keys == 'accessSecret' and params[keys]:
                    Envariable.set_task_sk(params[keys])
                if keys == 'file' and params[keys]:
                    Envariable.set_task_file(params[keys])
                if keys == 'task_id' and params[keys]:
                    Envariable.set_task_id(params[keys])
            return True
        except Exception as e:
            logging.info('{"Error": "Check Params Func {}"}'.format(e))
            return

class RefreshTask(object):

    @staticmethod
    def Query_Task_Progress():
        logging.info("in ->>>>>>>>> Query_Task_Progress")
        try:
            client = AcsClient(Envariable.get_task_ak(), Envariable.get_task_sk(), Envariable.REGION)
            task_query_request = DescribeRefreshTasksRequest()
            task_query_request.set_accept_format('json')
        except Exception as e:
            logging.info("task_query_request {}".format(e))
            return

        logging.info("Query_Task_Progress {}".format(Envariable.task_doing))
        for value in Envariable.task_doing:
            timeout = 0
            while True:
                count = 0
                task_query_request.set_TaskId(int(value))
                logging.info("[" + value + "]" + "is doing... ...")
                task_query_response = json.loads(client.do_action_with_exception(task_query_request).decode('utf-8'))
                for t in task_query_response['Tasks']['CDNTask']:
                    if t['Status'] != 'Complete':
                        count += 1
                if count == 0:
                    logging.info("in ->>>>>>>>> count")
                    Envariable.task_success_id.append(value)
                    logging.info("[" + value + "]" + "is finish")
                    break
                elif timeout >= 1:
                    logging.info("in ->>>>>>>>> timeout")
                    MSS = "timeout TaskID: " +value
                    Envariable.task_fail_id.append(MSS)
                    logging.info("[" + value + "]" + "timeout")
                    break
                else:
                    timeout += 1
                    time.sleep(3)
                    continue
        if len(Envariable.task_success_id) <=0 and len(Envariable.task_fail_id) <= 0:
            MysqlJDBC.UPDATE_FAIL_STATUS("TaskID is Null", Envariable.task_id)
        if len(Envariable.task_success_id) > 0:
            print("success", Envariable.task_success_id)
            MysqlJDBC.UPDATE_SUCCESS_STATUS(','.join(set(Envariable.task_success_id)), Envariable.task_id)
            Envariable.task_success_id = []
        if len(Envariable.task_fail_id) > 0:
            print("failed", Envariable.task_fail_id)
            MysqlJDBC.UPDATE_FAIL_STATUS(','.join(set(Envariable.task_fail_id)), Envariable.task_id)
            Envariable.task_fail_id = []

        return

    # TODO Main function
    @staticmethod
    def Main(PARAMETERS_KEYS):
        logging.info("in ->>>>>>>>> Main")
        Refresh_Check = Check_Params().Checking(PARAMETERS_KEYS)
        if not Refresh_Check: return
        if not BaseCheck().CheckQuota(): return

        for g in doTask.doProd():
            Envariable.url_list = []
            Envariable.retry = 0
            doTask.doRefresh(''.join(g))
            time.sleep(1)

        try:
            if len(Envariable.task_doing) > 0 or len(Envariable.task_fail_id) > 0:
                print("doing", Envariable.task_doing,Envariable.task_fail_id)
                MysqlJDBC.UPDATE_DOING_STATUS(','.join(set(Envariable.task_doing)) or 0,Envariable.task_fail_id or 0, Envariable.get_task_id())
        except Exception as e:
            logging.info('{"Error": "Main Insert doing task failed {}" }'.format(e))
        RefreshTask.Query_Task_Progress()
