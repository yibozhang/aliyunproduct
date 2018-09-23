
### PutObject 脚本环境基础 2.7.5 来编写，如移植到各位客户机器上有异常，请看下对应的库文件，或者兼容性问题。

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

    . 客观想要玩的 安全，可以加个`外套 Content-MD5`，但是不注意的人就会忘记加了，补充如下：根据协议 RFC 1864 对消息内容（不包括头部）计算 MD5 值获得 128 比特位数字，对该数字进行 `base64` 编码为一个消息的 Content-MD5 值，并且 `MD5` 是 `大写` 哦。

    . 如果客观想要单独加项目 CanonicalizedOSSHeaders 一定要记得不仅在 Header 中加，你的 hmac 计算时也要加，来个板 “例” Content-Type 一定要在 hmac 计算中
     hmac.new("5Lic5Lqs5LiA54K56YO95LiN54Ot","PUT\n\napplication/x-www-form-urlencoded\nSun, 02 Sep 2018 03:20:05 GMT\nx-oss-video:tokhot.avi/zhangyibo/tokhot.avi", sha)

    . 如果遇到 client 计算的 MD5 和 Server 不一致的情况请直接使用 HTTPS 传输，很可能中间的网络设置有故障或者劫持时导致内存被篡改，只要将 url 改为 https:// 就是启动 HTTPS 协议 上传/ 下载 了。

   

### AnalysisCors.py 脚本环境基础 2.7.5 来编写，如移植到各位客户机器上有异常，请看下对应的库文件，或者兼容性问题。

## 注意：使用之前请 pip install oss2 安装 OSS 模块
