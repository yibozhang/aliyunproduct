#!/bin/bash

# 图片处理报错时可以用这个 功能验证 原图是否损坏
# 安装 imagemagick
convert $1 -resize 100x100 ./dest_$1
