#!/usr/bin/env python
#coding=utf-8
import json
import time

from aliyunsdkcdn.request.v20180510.DescribeDomainCertificateInfoRequest import DescribeDomainCertificateInfoRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdklive.request.v20161101.DescribeLiveDomainCertificateInfoRequest import \
    DescribeLiveDomainCertificateInfoRequest

credentials = AccessKeyCredential('AK', 'SK')

# use STS Token 
# credentials = StsTokenCredential('<your-access-key-id>', '<your-access-key-secret>', '<your-sts-token>')
client = AcsClient(region_id='cn-shanghai', credential=credentials)

# 域名存放文件每行一个域名
with open('/Users/hanli.zyb/log/nosdn.txt', 'r', encoding='UTF-8') as file:
    recv_a=file.readlines()

fl = open('/Users/hanli.zyb/ffmpeg/yunxin3.txt','a+',encoding='UTF-8')

for i in recv_a:
        try:

            request = DescribeDomainCertificateInfoRequest()
            request.set_accept_format('json')
            request.set_DomainName(i.strip('\n').strip(''))
            response = client.do_action_with_exception(request)
            cernamt = json.loads(response)['CertInfos']['CertInfo'][0]['CertName']
            print("%s \t\t -> %s\n"%(i.strip('\n'),cernamt))
            fl.write("%s \t\t -> %s\n"%(i.strip('\n'),cernamt))
        except Exception as e:
            fl.write("%s \t\t -> %s\n" % (i.strip('\n'), str(e)))
