let OSS = require('ali-oss')

let client = new OSS({
  region: 'oss-cn-shenzhen',
  accessKeyId: '',
  accessKeySecret: '',
  bucket: 'hanli-shenzhen'
});


client.put('test.txt', 'test.txt',{
  callback: {
  url: 'http://47.106.91.186:5000/wsgi',
  body: 'bucket=${bucket}&object=${object}&var1=${x:var1}',
  customValue: {
    var1: 'value1',
    var2: 'value2',
  },
},
}).then((res)=>{
    console.log(res);
}).catch(err=>{
    console.log(err)
})

//异步上传+回调+自定义变量
