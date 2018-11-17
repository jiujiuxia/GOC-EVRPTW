
#args step2
step2=/home/jiuxia/vrp/model/group.py
step3=/home/jiuxia/vrp/model/solver.py
root3=/home/jiuxia/vrp/step3out
root2=/home/jiuxia/vrp/step2out

allcmd=/home/jiuxia/vrp/model/allcmd.sh
host=/home/jiuxia/vrp/model/host.txt

in=$1
out2=$2
groupnum=$3
smallgroup=$4
groupstandard=$5
instep1=$6
python ${step2} ${in} ${out2} ${groupnum} ${smallgroup} ${groupstandard} ${instep1}


