#!/usr/bin/python
#****************************************************************#
# ScriptName: MysqlJDBC.py
# Author: $SHTERM_REAL_USER@alibaba-inc.com
# Create Date: 2021-08-08 15:53
# Modify Author: $SHTERM_REAL_USER@alibaba-inc.com
# Modify Date: 2021-08-08 15:53
# Function:
#***************************************************************#
import mysql.connector
import logging
import time

class MysqlJDBC(object):

    AUTH_KEY = {"host": "rm-bo.mysql.rds.aliyuncs.com",
                "user": "hanli",
                "password": "",
                "database": ""}

    # TODO Insert Doing task
    @staticmethod
    def INSERT_TASK(PARAMETER_KEY):
        try:
            CONN = mysql.connector.connect(host=MysqlJDBC.AUTH_KEY['host'], user=MysqlJDBC.AUTH_KEY['user'],
                                           password=MysqlJDBC.AUTH_KEY['password'], database=MysqlJDBC.AUTH_KEY['database'],connect_timeout=10)
            CURSOR = CONN.cursor()
            TASK_TIME = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime())
        except Exception as e:
            return "INSERT TASK Failed {}".format(e)

        # clear task
        if PARAMETER_KEY['RefreshOrPreheat'] == 'clear':

            INSERT_VALUE = (PARAMETER_KEY['task_id'],
                            PARAMETER_KEY['accessSecret'],
                            PARAMETER_KEY['accessKeyId'],
                            PARAMETER_KEY['file'],
                            PARAMETER_KEY['RefreshOrPreheat'],
                            PARAMETER_KEY['ObjectType'],
                            TASK_TIME,
                            "doing")
            INSERT_SQL = '''INSERT INTO producetask (task_id,accessSecret,accessKeyId,file,RefreshOrPreheat,ObjectType,task_time,progress) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''

        # push task
        if PARAMETER_KEY['RefreshOrPreheat'] == 'push':
            INSERT_VALUE = (PARAMETER_KEY['task_id'],
                            PARAMETER_KEY['accessSecret'],
                            PARAMETER_KEY['accessKeyId'],
                            PARAMETER_KEY['file'],
                            PARAMETER_KEY['RefreshOrPreheat'],
                            PARAMETER_KEY['Area'],
                            TASK_TIME,
                            "doing")
            INSERT_SQL = '''INSERT INTO producetask (task_id,accessSecret,accessKeyId,file,RefreshOrPreheat,ObjectType,task_time,progress) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
        try:
            CURSOR.execute(INSERT_SQL, INSERT_VALUE)
            CONN.commit()
            CURSOR.close()
            CONN.close()
            return True
        except Exception as e:
            return "INSERT TASK Failed {}".format(e)



    # UPDATE_FAIL_STATUS
    @staticmethod
    def UPDATE_FAIL_STATUS(fail_task,task_id):
        try:
            CONN = mysql.connector.connect(host=MysqlJDBC.AUTH_KEY['host'], user=MysqlJDBC.AUTH_KEY['user'],
                                           password=MysqlJDBC.AUTH_KEY['password'],
                                           database=MysqlJDBC.AUTH_KEY['database'])
            CURSOR = CONN.cursor()
        except Exception as e:
            logging.info("UPDATE_FAIL_STATUS Func {}".format(e))
            return

        # doing
        try:
            UPDATE_SQL = "UPDATE producetask set fail_task = '{0}', doing_task = 0, progress = 'failed' WHERE task_id = '{1}'".format(fail_task,task_id)
            CURSOR.execute(UPDATE_SQL)
            CONN.commit()
            CURSOR.close()
            CONN.close()
            return True
        except Exception as e:
            logging.info("UPDATE_FAIL_STATUS Commit Failed {}".format(e))
            return

    # UPDATE_DOING_STATUS
    @staticmethod
    def UPDATE_DOING_STATUS(doing_task, fail_task, task_id):
        try:
            CONN = mysql.connector.connect(host=MysqlJDBC.AUTH_KEY['host'], user=MysqlJDBC.AUTH_KEY['user'],
                                           password=MysqlJDBC.AUTH_KEY['password'],
                                           database=MysqlJDBC.AUTH_KEY['database'])
            CURSOR = CONN.cursor()
        except Exception as e:
            logging.info("UPDATE_SUCCESS_STATUS fun {}".format(e))
            return

        # doing
        try:
            UPDATE_SQL = "UPDATE producetask set doing_task = '{0}', fail_task = '{1}' WHERE task_id = '{2}'".format(doing_task, fail_task, task_id)
            CURSOR.execute(UPDATE_SQL)
            CONN.commit()
            CURSOR.close()
            CONN.close()
            return True
        except Exception as e:
            logging.info("UPDATE_FAIL_STATUS Commit Failed {}".format(e))
            return

    # UPDATE_SUCCESS_STATUS
    @staticmethod
    def UPDATE_SUCCESS_STATUS(success_task, task_id):
        try:
            CONN = mysql.connector.connect(host=MysqlJDBC.AUTH_KEY['host'], user=MysqlJDBC.AUTH_KEY['user'],
                                           password=MysqlJDBC.AUTH_KEY['password'],
                                           database=MysqlJDBC.AUTH_KEY['database'])
            CURSOR = CONN.cursor()
        except Exception as e:
            logging.info("UPDATE_SUCCESS_STATUS fun {}".format(e))
            return

        # doing
        try:
            UPDATE_SQL = "UPDATE producetask set success_task = '{0}', doing_task = 0, progress = 'success' WHERE task_id = '{1}'".format(success_task, task_id)
            CURSOR.execute(UPDATE_SQL)
            CONN.commit()
            CURSOR.close()
            CONN.close()
            return True
        except Exception as e:
            logging.info("UPDATE_FAIL_STATUS Commit Failed {}".format(e))
            return

    # TODO QUERY TASK RESULT
    @staticmethod
    def QUERY_TASK_RESULT(task_time,task_id):
        try:
            CONN = mysql.connector.connect(host=MysqlJDBC.AUTH_KEY['host'], user=MysqlJDBC.AUTH_KEY['user'],
                                           password=MysqlJDBC.AUTH_KEY['password'],
                                           database=MysqlJDBC.AUTH_KEY['database'])
            CURSOR = CONN.cursor()
        except Exception as e:
            return {"Error": "connect mysql failed {}".format(e)}

        try:
            QUERY_SQL = "select task_time,task_id,doing_task,progress,fail_task,success_task from producetask where task_id='{0}' and task_time like '{1}%'".format(task_id,task_time)
            CURSOR.execute(QUERY_SQL)
            QUERY_RESULT = CURSOR.fetchall()
            CURSOR.close()
            CONN.close()
            if QUERY_RESULT:
                return QUERY_RESULT
            else:
                return {"Error": "JDBC QUERY TASK {0} RESULT is Null or other reasons".format(task_id)}
        except Exception as e:
            logging('Error JDBC QUERY TASK RESULT Faile {}'.format(e))
            return str(e)
