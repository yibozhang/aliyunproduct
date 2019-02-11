#!/bin/bash
# -*- coding:utf8 -*-
# autor:hanli.zyb

RL="\033[31m"
RR="\033[0m"
LOG="$(pwd)/check_result.log"

# 获取容器
function GET_DOCKER_CONTAINER() {

  echo -e "$RL============GET_DOCKER_CONTAINER===========$RR" >$LOG
  CONTAINERID=($(docker ps -f label=edas.appid=${APPID} -f label=edas.component=app | awk 'NR==2{print $1,$2}'))

  if [ ${#CONTAINERID[*]} -eq 2 ]; then
   echo ${CONTAINERID[@]} >>$LOG
   GET_DOCKER_SCRIPT
  else
   echo "No Container's ID found" > checklog.&& exit 1
  fi
  
}

# 获取启动脚本
function GET_DOCKER_SCRIPT() {

  echo -e "$RL============GET_DOCKER_SCRIPT==============$RR" >> $LOG
  STARTSCRIPT=$(docker inspect ${CONTAINERID[0]} -f {{.Config.Cmd}} | tr -d '[|]' 2>&1)
  echo ${STARTSCRIPT} >> $LOG && GET_DOCKER_LOGS
}

# 获取运行日志
function GET_DOCKER_LOGS() {
 
  echo -e "$RL============GET_DOCKER_LOGS================$RR" >> $LOG
  docker logs ${CONTAINERID[0]} >> $LOG

  echo -e "$RL============GET_VIPSERVER_LOGS=============$RR" >> $LOG
  if [ -f "/home/admin/${APPID}/root/logs/vipsrv-logs/vipclient.log" ]; then
    cat /home/admin/${APPID}/root/logs/vipsrv-logs/vipclient.log >>$LOG
  else
    echo "No VIPSERVER log found!" >>$LOG
  fi

  echo -e "$RL============GET_CATALINA_LOG===============$RR" >> $LOG
  TAOBAO=$(ls /home/admin/b88fd5c6-0a9e-4235-8807-24716ff2b9d0/home/admin/ | grep "tao")

  if [ "${TAOBAO}" == "" ]; then
    echo "No catalina.out found!" 
  else
    if [ -f "/home/admin/${APPID}/home/admin/${TAOBAO}/logs/catalina.out" ]; then
      cat /home/admin/${APPID}/home/admin/${TAOBAO}/logs/catalina.out >>$LOG
    fi
  fi

  echo -e "$RL============GET_EDASTRACE_LOG==============$RR" >> $LOG
  if [ -f "/home/admin/edas/script/logs/edas.action.trace" ]; then
    cat /home/admin/edas/script/logs/edas.action.trace >>$LOG
  else
    echo "No edas.action.trace found!"
  fi

  GET_DOCKER_ENV

}

# 获取环境变量
function GET_DOCKER_ENV() {
  echo -e "$RL============GET_DOCKER_ENV=================$RR" >> $LOG
  docker inspect ${CONTAINERID[0]} >> $LOG
}

# 进入检查模式
function CHECK_START_FAILD() {

  local PORT=$(docker ps | egrep -o "0.*tcp" | awk -F- '{print $1}' | awk -F: '{print $2}' 2>&1)
  
  echo -e "$RL============CHECK_DOCKER_PORT================$RR"
  if [ ${PORT} == "" ]; then
    echo "check docker faild"
  else
    echo "check docker port success"
    RESULT=$(curl -v 127.0.0.1:${PORT}/_ehc.html 2>&1 | egrep "404|200")
    echo -e "$RL============CHECK_DOCKER_HEALTH==============$RR"
    if [ "${RESULT}" == "" ]; then
      echo "check docker health faild"
    else
      echo "check docker health success"
    fi
  fi

  local CONTAINERID=($(docker ps -f label=edas.appid=${APPID} -f label=edas.component=app | awk 'NR==2{print $1,$2}'))
  local STARTSCRIPT=$(docker inspect ${CONTAINERID[0]} -f {{.Config.Cmd}} | tr -d '[|]' 2>&1)
  local CONTAINER=$(docker run -d --net=host --entrypoint='/bin/bash' ${CONTAINERID[1]} -c "sleep 2000")
  
  echo -e "$RL============DOCKER_START_LOG=================$RR" 
  docker exec -it ${CONTAINER} bash -c "/bin/bash ${STARTSCRIPT}"
   
}

while getopts ":a:m:" opt
do
  case $opt in
    a)
      APPID=$OPTARG && GET_DOCKER_CONTAINER
      ;;
    m)
      APPID=$OPTARG && CHECK_START_FAILD
      ;;
    *)
      echo "No terminal args found ! Please use -h"
    ;;
  esac
done
