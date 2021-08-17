#!/usr/bin/python
#****************************************************************#
# ScriptName: WebRefreshTask.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2021-08-08 15:49
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2021-08-08 15:49
# Function:
#***************************************************************#
import uuid
import logging
import threading
import tornado.ioloop
import tornado.web
import tornado.options
from RefreshTask import *
from MysqlJDBC import *
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
tornado.options.parse_command_line()

class NoBlockingHnadler(tornado.web.RequestHandler,threading.Thread):
    # 线程池
    executor = ThreadPoolExecutor(5)
    # 入库参数
    PARAMETERS_KEYS = {}

    def options(self):
        self.set_header('Access-Control-Allow-Methods','*')
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Credentials','true')
        self.set_header('Access-Control-Allow-Headers','*')
        self.write('ok.')
        self.flush()
        return

    @run_on_executor
    def Refresh(self):
        RefreshTask.Main(NoBlockingHnadler.PARAMETERS_KEYS)

    @tornado.gen.coroutine
    def Middle(self):
        result = yield self.Refresh()

    @tornado.gen.coroutine
    def post(self):
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers','*')
        try:
            formdata = json.loads(self.request.body.decode("utf-8"))
            logging.info('NoBlockingHnadler POST: {0}'.format(formdata))
        except Exception as e:
            self.write('Post formdata to jsonload error {0}'.format(e))

        # TODO check transfer data valid
        check_result = self.Check_Data_Format(formdata)
        try:
            if check_result != True:
                self.set_status(400)
                self.write(check_result)
                return
        except Exception as e:
            self.set_status(400)
            self.write({"Error": "{}".format(e)})
            return

        # input mysql
        try:
            NoBlockingHnadler.PARAMETERS_KEYS['task_id'] = self.request.uri[5:] + '-' + str(uuid.uuid1())
            sql_result = MysqlJDBC.INSERT_TASK(NoBlockingHnadler.PARAMETERS_KEYS)
            if sql_result == True:
                resp = self.Middle()
                self.write({"Info": "task_id {0}".format(NoBlockingHnadler.PARAMETERS_KEYS['task_id'])})
                return
            else:
                self.set_status(400)
                self.write({"Error": "refresh {}".format(sql_result)})
                return
        except Exception as e:
            self.set_status(400)
            self.write({"Error": "{}".format(e)})
            return

    # check data valid
    def Check_Data_Format(self,formdata):
        try:
            # accessSecret
            if 'accessSecret' in formdata.keys() and formdata['accessSecret']:
                NoBlockingHnadler.PARAMETERS_KEYS['accessSecret'] = formdata['accessSecret']
            else:
                return '{"Error": "The parameter accessSecret is missing or the value is empty"}'
            # accessKeyId
            if 'accessKeyId' in formdata.keys() and formdata['accessKeyId']:
                NoBlockingHnadler.PARAMETERS_KEYS['accessKeyId'] = formdata['accessKeyId']
            else:
                return '{"Error": "The parameter accessKeyId is missing or the value is empty"}'
            # file
            if 'file' in formdata.keys() and formdata['file']:
                NoBlockingHnadler.PARAMETERS_KEYS['file'] = formdata['file']
            else:
                return '{"Error": "The parameter file is missing or the value is empty"}'
            # RefreshOrPreheat
            if 'RefreshOrPreheat' in formdata.keys() and formdata['RefreshOrPreheat'] in ('push','clear'):
                NoBlockingHnadler.PARAMETERS_KEYS['RefreshOrPreheat'] = formdata['RefreshOrPreheat']
            else:
                return '{"Error": "The parameter RefreshOrPreheat is missing or the value is empty"}'
            # push or clear
            if 'Area' in formdata.keys() and 'ObjectType' in formdata.keys():
                return '{"Error": "Area ObjectType cannot appear at the same time"}'
            if formdata['RefreshOrPreheat'] == 'push':
                if 'Area' in formdata.keys() and formdata['Area'] in ('domestic', 'overseas'):
                    NoBlockingHnadler.PARAMETERS_KEYS['Area'] = formdata['Area']
                else:
                    return '{"Error": "The parameter Area is missing or the value is empty"}'
            elif formdata['RefreshOrPreheat'] == 'clear':
                if 'ObjectType' in formdata.keys() and formdata['ObjectType'] in ('File', 'Directory'):
                    NoBlockingHnadler.PARAMETERS_KEYS['ObjectType'] = formdata['ObjectType']
                else:
                    return '{"Error": "Parameter ObjectType or empty"}'
            else:
                return '{"Error": "push or clear unknow error"}'
            return True
        except Exception as e:
            return str(e)



class UploadFileHandler(tornado.web.RequestHandler):

    def options(self):
        self.set_header('Access-Control-Allow-Methods','*')
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Credentials','true')
        self.set_header('Access-Control-Allow-Headers','*')
        self.write('ok.')
        self.flush()
        return

    # TODO upload file
    def post(self):
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers','*')

        try:
            if self.request.files.get:
                url_file = self.request.files['file'][0]
                if url_file:
                    timestamp = str(int(round(time.time() * 1000)))
                    file_name = "/mnt/logs/" + timestamp + '_' + url_file['filename']
                    save_file = open(file_name, "w")
                    save_file.write(str(url_file['body'], encoding='utf8'))
                    save_file.close()
                    self.write({'code': 0, 'msg': file_name })
                else:
                    self.write({"Error": "Upload File Failed"})
                return
        except Exception as e:
            self.set_status(400)
            self.write({"Error": str(e)})
            return

class QueryTaskHandler(tornado.web.RequestHandler):

    def options(self):
        self.set_header('Access-Control-Allow-Methods','*')
        self.set_header('Access-Control-Allow-Origin','*')
        self.set_header('Access-Control-Allow-Credentials','true')
        self.set_header('Access-Control-Allow-Headers','*')
        self.write('ok.')
        self.flush()
        return

    def post(self):
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers','*')

        Query_Result = {}
        try:
            formdata = json.loads(self.request.body.decode("utf-8"))
            task_time = formdata['task_time']
            task_id = formdata['task_id']
            if task_id and task_time:
                Query_Result['taskresult'] = MysqlJDBC.QUERY_TASK_RESULT(task_time,task_id)
                print(Query_Result)
                if Query_Result:
                    self.write(Query_Result)
                    self.flush()
                    return
                else:
                    self.set_status(400)
                    self.write(Query_Result)
                    self.flush()
                    return
        except Exception as e:
            self.set_status(400)
            self.write({"Error":str(e)})
            return

def make_app():
    return tornado.web.Application([
        (r"/cdn/refresh", NoBlockingHnadler),
        (r"/cdn/uploadfile", UploadFileHandler),
        (r"/cdn/querytask",QueryTaskHandler),
    ], autoreload=True)

if __name__ == "__main__":
    app = make_app()

    app.listen(80)

    tornado.ioloop.IOLoop.current().start()
