
#环境基础 2.7.5 来编写，如移植到各位客户机器上有异常，请看下对应的库文件，或者兼容性问题。

     $PSA1#: python PutObject.py -h
     Usage: beiwo.py [options]

     Options:

      -h, --help  show this help message and exit
      -i AK       Must fill in Accesskey          访问云产品的 Accesskey
      -k SK       Must fill in AccessKeySecrety   访问云产品的 Accesskey Secret
      -e ED       Must fill in endpoint           OSS 的 endpoint 地理信息
      -b BK       Must fill in bucket             OSS bucket 
      -o OBJECTS  File name uploaded to oss       上传的 object 名称
      -f FI       Must fill localfile path        本地文件的名称
