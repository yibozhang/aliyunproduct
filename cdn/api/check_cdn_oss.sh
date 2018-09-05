#!/bin/bash
#-*- coding: utf-8 -*-
# author: hanli
# describe: 在 LINUX 端上执行用来检查初步的排障信息。适用于 CDN+OSS 的服务场景
# Initial variable
# update: 2018-01-17

DOMAIN=$1
REQURL=$2
ENDPOINT=$3
LGREE="\033[32m"
LRED="\033[31m"
RGREE="\033[0m"
RESULT=""
CODE=""
STATUS=""
CACHE=""

# 检查脚本输入参数
function Judge(){
             
  local DOMAINS="www.zhangyb.mobi"
  local REQURLS="http://www.zhangyb.mobi/index.html"
  local ENDPOINTS="ali-beijing.oss-cn-beijing.aliyuncs.com"
    
  if [ $1 -ne 3 ]; then
    echo -e "${LRED}Usge${RGREE}: $0 ${DOMAINS} ${REQURLS} ${ENDPOINTS}" && exit 1
  fi
  CheckEnvoirment
}   

# 检查本机依赖环境
function CheckEnvoirment(){
  echo -e "${LGREE}INFO: CHECKING SCRIPTS DENPENDENT ENVIORMENT... ${RGREE}"
  which sed >/dev/null 2>&1 && DealWith sed || echo -e "${LRED}INFO: THE SED CANNOT BE USE, START USE AWK${RGREE}"
  which awk >/dev/null 2>&1 && DealWith awk || echo -e "${LRED}INFO: THE AWK CANNOT BE USE${RGREE}"
  echo -e "${LRED}INFO: UNABLE FIND SCRIPTS DEPENDENT ENVIORMENT！！！${RGREE}" && exit 1
}

function DealWith(){

  if [ "$1" == "sed" ]; then
    OSSURL=$(echo ${REQURL} | sed -r 's/(http\:\/\/)([^\/]*)(\/.*)/\1'${ENDPOINT}'\3/' 2>&1 )
  elif [ "$1" == "awk" ]; then
    OSSURL=http://${ENDPOINT}$(echo ${REQURL} | awk -F"//" '{print $2}' | awk -F "/" '{print "/"$2}' 2>&1)
  else
    echo "${LRED}INFO: GET OSS URL ERROR！！！${RGREE}" && exit 1
  fi
  CheckPing
}    

# 开始各项检查
function CheckPing(){
  
  echo -e "${LGREE}INFO: CHECKING NETWORKING...${RGREE}"
  ping www.taobao.com -w 4 -d >/dev/null 2>/dev/null
  [ "$?" != "0" ] && echo -e "${LGREE}INFO: MACHINE NETWORKING FAILURE${RGREE}" && exit 1

  echo -e "${LGREE}INFO: NETWORK IS GOOD ${DOMAIN} CHECKING...${RGREE}"
  ping ${DOMAIN} -w 4 -d >/dev/null 2>/dev/null
  [ "$?" != "0" ] && echo -e "${LGREE}INFO: DOMAIN ${DOMAIN} NETWORK FAILURE${RGREE}"

  echo -e "${LGREE}INFO: OSS DOMAIN ${ENDPOINT} CHECKING...${RGREE}"
  ping ${ENDPOINT} -w 4 -d >/dev/null 2>/dev/null
  [ "$?" != "0" ] && echo -e "${LGREE}INFO: OSS ${ENDPOINT} NETWORK FAILURE${RGREE}"

  Check 
}
 
function Check(){

  if GetInfo; then
    echo -e "${LGREE}INFO: ${RESULT}${RGREE}"
  fi

  if GetDomain; then
    echo -e "${LGREE}INFO: CHECK WORK LEGAL${RGREE}"
  else
    echo -e "${LRED}INFO: DOMAIN SERVICE NOT IN ALIBABA${RGREE}" && exit 1
  fi

  if GetCurl; then
    echo -e "${LGREE}INFO: URL HTTP CODE ${STATUS}, CACHE TIME ${CACHE}${RGREE}"
  else
    echo -e "${LRED}INFO: CHECK CDN DOMAIN WORK IS FAILURE${RGREE}"
  fi

  if GetOSS; then
    echo -e "${LGREE}INFO: OSS IS WORK GOOD${RGREE}"
  else
    echo -e "${LRED}INFO: OSS IS WORK FAILURE${RGREE}"
  fi
  exit 0
}

# 测试 CDN 访问连通性
function GetCurl(){

  CODE=$(curl -svo /dev/null ${REQURL} -m 2 2>&1 | egrep -i "HTTP\/[1|2]\.[0|2|1] .*" | fgrep 200)

  if [ ! -z "${CODE}" ]; then
    STATUS=$(curl -svo /dev/null ${REQURL} -m 2 2>&1 | grep -i "x-cache" | grep -i hit >/dev/null && echo "HIT" || echo "MISS")
    CACHE=$(curl -svo /dev/null ${REQURL} -m 2 2>&1 | grep -i "X-Swift-CacheTime" | awk '{print $3}')
    return 0
  fi
  return 1
}

# 测试 OSS 访问连通性
function GetOSS(){
  local OSSCODE=$(curl -svo /dev/null ${OSSURL} -H "Host: ${DOMAIN}" -m 2 2>&1 | egrep -i "HTTP\/[1|2]\.[0|2|1] .*" | fgrep 200)
  local OSSRESP=$(curl -sv0 /dev/null ${OSSURL} -m 2 2>&1 | egrep -i "HTTP\/[1|2]\.[0|2|1] .*" | fgrep 200)
  [ ! -z "${OSSCODE}" ] || [ ! -z "${OSSRESP}" ] && return 0 || return 1
}

# 获取本地的 DNS CLIENT IP
function GetInfo(){

  local TIMESTART=$(date +%s)
  local TIMEEND=$(date +%s)
  local URL="https://42-120-74-167-408161718.dns-detect.alicdn.com/api/cdnDetectHttps"
  local METHOD="commitDetectHttps"
  local DETECTID="408161718"
  local JQUERY="jQuery110104439492578113773"
  local INFO=$(curl -v "${URL}?method=${METHOD}&detectId=${DETECTID}&cb=${JQUERY}_${TIMESTART}&_=${TIMEEND}" 2>&1 | xargs | awk '{print $NF}')

  if [ ! -z "${INFO}" ]; then
    RESULT=$(echo ${INFO} | egrep -o "ldns\:.*\,localIp\:[^}]*")
    [ ! -z "${RESULT}" ] && return 0 || return 1
  fi
  return 1
}

# 判断是否有 CNAME 记录，是否在阿里云加速
function GetDomain(){

  local CNAME=$(dig ${DOMAIN} +time=1 2>&1 | fgrep CNAME | awk '{print $NF}' |fgrep kunlun)
  [ ! -z "${CNAME}" ] && return 0 || return 1
}


Judge $#
