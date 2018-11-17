time=`date +%Y%m%d%H%M%S`
root=/home/jiuxia/vrp/model
log=/home/jiuxia/vrp/logs
nohup bash ${root}/$1 >> ${root}/run$1${time}.log &
echo "$1    ${time}    $!" >> ${root}/pid
sleep 1
