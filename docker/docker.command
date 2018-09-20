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
