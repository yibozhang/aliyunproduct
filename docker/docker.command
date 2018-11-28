docker image ls 
列出镜像文件

docker info

docker version

systemctl status|start|stop|restart docker

docker image pull address
从一个地址上把 image 拉到本地

docker contains ls 
列出容器文件

docker container run -it imageid bash
从 image 文件生成一个容器 ID

docker ps -a 
查看当前运行的容器 ID

docker rm <容器 ID>  / docker container kill <容器 ID>
删除一个正在运行的容器文件

docker images -t
过滤列出的镜像

docker images -q
仅输出镜像 ID

docker tag REPOSITORY:TAG new_REPOSITORY:new_TAG
为镜像重新命名一个 TAG

docker rmi ImageID 
删除一个本地的镜像，如果正在运行的镜像是无法删除的。需要用 docker ps -a 找到运行的镜像，然后 docker rm iamgeID 即可


创建镜像

 1. 在已有镜像的基础上修改完 提交到仓库
 docker commit -m "commit message" <container_id> <repository:tag_imageid>
 docker commit -m "hello world" de3298bfcd17 docker.io/redis:1.0db23f46600bc

 2. 基础本地模板导入
 比如下载到本地一个 ubuntu 镜像，通过 import 的方式导入镜像
 cat ubuntu-14.4.minial.tar.gz | docket import - repository:tag

镜像的存入和导出

 1. 将镜像导出为本地文件 save
 docker save -o redis.tar.gz redis:4.0
