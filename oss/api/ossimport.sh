#!/bin/bash
# set import environment

#---------------------------function--------------------------

function check_expect()
{
    ret_val=$(expect -v)
    g_ret=$(echo $ret_val | grep 'expect version')
    if [ -n "$g_ret" ]; then
        echo $ret_val    
    else
        echo "please install expect: apt install expect or yum install expect"
        exit 1
    fi
}

function check_wget()
{
    ret_val=$(wget -V)
    w_ret=$(echo $ret_val | grep 'GNU Wget')
    if [ -n "$w_ret" ]; then
        echo ${w_ret%"linux-gnu"*}
    else
        echo "please install wget: apt install wget or yum install wget"
        exit 1
    fi
}

function check_pssh()
{
    pssh > fout 2>&1
    ret_val=$(cat fout | grep 'Usage: pssh')
    rm -rf fout
    if [ -n "$ret_val" ]; then
        return 0
    else
        return 1 
    fi
}

function scp_trans()
{
    dst_ip=$1
    user=$2
    password=$3
    src_path=$4
    dst_path=$5

    expect -c "
        spawn scp -P $port -r ${src_path} ${user}@${dst_ip}:${dst_path}
        expect {
            \"*assword\" {set timeout 30; send \"$password\r\"; exp_continue;}
            \"yes/no\" {send \"yes\r\"; exp_continue;}
        }"
    
   return $?
}

function download()
{
    obj=$1
    if [ -f "$HOME/mingdi/$obj" ]; then
        return 0
    fi
    
    wget http://gosspublic.alicdn.com/ossimport/tools/$obj -O $HOME/mingdi/$obj
    if [ ! -f "$HOME/mingdi/$obj" ]; then
        echo "wget $obj failed"
        exit 1
    fi
}

function untar()
{
    obj=$1
    tar -zxf $HOME/mingdi/$obj -C $HOME/mingdi/
    if [ ! -d "$HOME/mingdi/${obj%.tar.gz*}" ]; then
        echo "tar $obj failed"
        exit 1
    fi
}

#---------------------------main--------------------------

dst_ips="30.40.11.12"
port=22
user=baiyubin
passwd=Alibaba65683
src_path=$HOME/.ssh/authorized_keys
dst_path=$HOME/.ssh/authorized_keys
ossimport=ossimport-2.3.2.tar.gz

# check commands
check_expect
check_wget

echo "$(date '+%F %T') start..."

# gen rsa
echo "gen rsa key pair"
if [ ! -f "$HOME/.ssh/id_rsa" -o ! -f "$HOME/.ssh/id_rsa.pub" ]; then
    rm -rf $HOME/.ssh/id_rsa $HOME/.ssh/id_rsa.pub
    ssh-keygen -t rsa -f $HOME/.ssh/id_rsa -P ""
fi
echo "privateKeyFile is $HOME/.ssh/id_rsa"

if [ -f "$HOME/.ssh/authorized_keys" ]; then 
    mv $HOME/.ssh/authorized_keys $HOME/.ssh/authorized_keys.bak
fi
cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys

# TODO check ips

# scp authorized_keys
echo "scp authorized_keys"
for ip in $dst_ips; do
    ret_val=$(scp_trans $ip $user $passwd $src_path $dst_path)
    echo $ret_val
    ret_val=$(echo $ret_val | grep '100%')
    if [ -n "$ret_val" ] ; then
        echo "scp to $ip ok"
    else
        echo "scp to $ip failed"
    fi
done

# downdload tools
mkdir -p $HOME/mingdi
cd $HOME/mingdi

# install pssh
check_pssh
ret=$?
if [ $ret -eq 0 ]; then 
    echo "pssh version $(pssh --version)"
else
    echo "install pssh"
    download "pssh-2.3.1.tar.gz"
    untar "pssh-2.3.1.tar.gz" 
    export PATH=$PATH:$HOME/mingdi/pssh-2.3.1/bin
    
    check_pssh
    ret=$?
    if [ $ret -eq 0 ]; then
        echo "pssh install ok"
        echo "" >> $HOME/.bashrc
        echo 'export PATH=$PATH:$HOME/mingdi/pssh-2.3.1/bin' >> $HOME/.bashrc
    else
        echo "pssh install failed"
        exit 2
    fi
fi

# gen ips
echo "gen ips"
if [ -f "$HOME/mingdi/ips" ]; then
    mv $HOME/mingdi/ips $HOME/mingdi/ips.bak
fi

for ip in $dst_ips; do
    if [ "$port" == "22" ]; then
        echo "${user}@${ip}" >> $HOME/mingdi/ips
    else
        echo "${user}@${ip}:${port}" >> $HOME/mingdi/ips
    fi
done 

# mkdir mingdi
pssh -h $HOME/mingdi/ips -i "mkdir -p $HOME/mingdi"
# TODO check pssh/pscp result

# java
echo "install java"
download "jdk-8u101-linux-x64.tar.gz"
echo "scp jdk-8u101-linux-x64.tar.gz"
pscp -h $HOME/mingdi/ips $HOME/mingdi/jdk-8u101-linux-x64.tar.gz $HOME/mingdi/jdk-8u101-linux-x64.tar.gz
echo "untar jdk-8u101-linux-x64.tar.gz"
pssh -h $HOME/mingdi/ips -i "tar -zxf $HOME/mingdi/jdk-8u101-linux-x64.tar.gz -C $HOME/mingdi/"

echo "java env"
echo "" >> $HOME/.bashrc
echo "export JAVA_HOME=$HOME/mingdi/jdk1.8.0_101" >> $HOME/.bashrc
echo 'export JRE_HOME=${JAVA_HOME}/jre' >> $HOME/.bashrc
echo 'export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib' >> $HOME/.bashrc
echo 'export PATH=${JAVA_HOME}/bin:$PATH' >> $HOME/.bashrc

# ossutil
echo "down ossutil64"
download "ossutil64"
echo "scp ossutil64"
pscp -h $HOME/mingdi/ips $HOME/mingdi/ossutil64 $HOME/mingdi/ossutil64
echo "chmod +x ossutil64"
pssh -h $HOME/mingdi/ips -i "chmod +x $HOME/mingdi/ossutil64"
echo "" >> $HOME/.bashrc
echo "alias ossutil64='$HOME/mingdi/ossutil64'" >> $HOME/.bashrc

# distribute .bashrc
echo "scp .bashrc"
pscp -h $HOME/mingdi/ips $HOME/.bashrc $HOME/.bashrc

# ossimmprt
echo "get ossimport"
if [ ! -f "$HOME/mingdi/$ossimport" ]; then
    wget http://gosspublic.alicdn.com/ossimport/international/distributed/$ossimport -O $HOME/mingdi/$ossimport
    if [ ! -f "$HOME/mingdi/$ossimport" ]; then
        echo "wget $ossimport failed"
        exit 1
    fi
fi

if [ -d "$HOME/mingdi/ossimport" ]; then
    rm -rf $HOME/mingdi/ossimport.bak
    mv $HOME/mingdi/ossimport $HOME/mingdi/ossimport.bak
fi
mkdir -p $HOME/mingdi/ossimport

tar -zxf $HOME/mingdi/$ossimport -C $HOME/mingdi/ossimport
if [ ! -d "$HOME/mingdi/ossimport/bin" ]; then
    echo "tar $ossimport failed"
    exit 1
fi
echo "workingDir is $HOME/mingdi/ossimport/workdir"

# TODO update import's config
echo "config workers"
rm -rf $HOME/mingdi/ossimport/conf/workers 
for ip in $dst_ips; do
    echo "$ip" >> $HOME/mingdi/ossimport/conf/workers
done

echo "config sys.properties"
sys_props_path=$HOME/mingdi/ossimport/conf/sys.properties
sed -i "s#workingDir=/root/import#workingDir=$HOME/mingdi/ossimport/workdir#g" $sys_props_path
sed -i "s#privateKeyFile=#privateKeyFile=$HOME/.ssh/id_rsa#g" $sys_props_path
sed -i "s/workerMaxThroughput(KB\/s)=100000000/workerMaxThroughput(KB\/s)=0/g" $sys_props_path
sed -i "s/workerUserName=root/workerUserName=$user/g" $sys_props_path
sed -i "s/workerPassword=\*\*\*\*\*\*/workerPassword=/g" $sys_props_path
sed -i "s/sshPort=22/sshPort=$port/g" $sys_props_path
sed -i "s/javaHeapMaxSize=1024m/javaHeapMaxSize=2g/g" $sys_props_path

echo "$(date '+%F %T') completed"

exit 0
