let OSS = require('ali-oss')
var fs = require('fs');
var path = require('path');

let client = new OSS({
  region: 'oss-cn-hangzhou',
  accessKeyId: '',
  accessKeySecret: '',
  bucket: 'gdc-hangzhou'
});

function travel(dir,callback) {
  fs.readdirSync(dir).forEach(function (file) {
    var pathname = path.join(dir,file);

    if (fs.statSync(pathname).isDirectory()) {
      travel(pathname,callback);
    } else {
      callback(file,pathname);
    }
  });
}
travel('/Users/hanli/localprogram/dist',async function (file,pathname) {

  try {
    console.log(file,pathname);
  } catch (e) {
  	console.log(er);
  }    

 });

//循环上传目录下的文件
