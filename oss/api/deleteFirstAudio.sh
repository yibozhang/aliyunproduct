#!/bin/bash

dir=$(ls -l ./ |awk '!/^d/ {print $NF}' |grep -i "\.mp4" )
 
for files in $dir
do
    echo "${files%.*}"
    ffmpeg -v quiet -i $files -map 0:v:0 -map 0:a:1 -c copy "OUT_${files%.*}".mp4 -y
done 
