## 使用方法：

* 1、先要按照 CDN  SDK 模块：pip install aliyun-python-sdk-cdn
* 2、再安装阿里云核心 SDK 模块：pip install aliyun-java-sdk-core
* 3、在 python 2.75 以上的环境运行；
* 安装成功后，脚本帮助参数 python $scripte -h

```
script options explain:             
	 -i <AccessKey>       访问阿里云凭证，访问控制台上可以获得；             
	 -k <AccessKeySecret> 访问阿里云秘钥，访问控制台上可以获得；             
	 -r <filename>        文件名称，每行一条 URL，有特殊字符先做 URLencode，以 http/https 开头；             
	 -t <taskType>        任务类型 clear 刷新，push 预热；             
	 -n [nums,[..100]]    每次操作文件数量，做多 100 条；
```
