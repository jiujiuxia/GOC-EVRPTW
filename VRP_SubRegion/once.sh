#path
step1=/home/jiuxia/vrp/model/cluster.py
step2=/home/jiuxia/vrp/model/group.py
step4=/home/jiuxia/vrp/model/standard.py
root=/home/jiuxia/vrp/step1out
root2=/home/jiuxia/vrp/step2out
root3=/home/jiuxia/vrp/step3out
root4=/home/jiuxia/vrp/step4out
in=/home/jiuxia/vrp/input
allcmd=/home/jiuxia/vrp/model/allcmd.sh
host=/home/jiuxia/vrp/model/host.txt

#host
mainhost=192.168.12.113
hosts=("192.168.12.116" "192.168.12.115" "192.168.12.113");

#输出发给其他电脑
deliverout(){
    deout=$1
    for((i=0;i<3;i++))
    do
        scp -r ${mainhost}:${deout}/* ${hosts[i]}:${deout}
    done
}
#step2
#name=5_-0.5_-0.8_-1.200000_3_first_receive_tm
#name=5_-0.5_-0.770000_-1.200000_3_first_receive_tm
#name=5_-0.5_-0.740000_-1.250000_3_first_receive_tm
#name=5_-0.5_-0.710000_-1.350000_4_first_receive_tm
name=5_-0.470000_-0.770000_-1.400000_3_first_receive_tm
out2=${root2}/${name}
echo "创建在各个电脑上创建第二步输出文件夹${out2}"
bash ${allcmd} ${host} mkdir ${out2}
echo "文件夹创建完成,将已有输出复制到其他电脑 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
deliverout ${out2}
#step3
out3=${root3}/${name}
echo "创建在各个电脑上创建第三步输出文件夹${out3}"
bash ${allcmd} ${host} mkdir ${out3}
echo "开始并行执行第三步 name=${name} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
groupnum=6
smallgroup=3
for((i=0;i<groupnum;i++))
do
    for((j=0;j<smallgroup;j++))
    do
	id2=`expr ${i} \* ${smallgroup}`
 	id2=`expr ${id2} + ${j}`
	echo "${id2}"
	id2=`expr ${id2} % 3`
	echo ${id2}
        echo "hostid=${hosts[${id2}]} name=${name}_${i}_${j}"
	ssh -n ${hosts[${id2}]} nohup bash /home/jiuxia/vrp/model/runstep3.sh ${i} ${j} ${out2} ${name} >> /home/jiuxia/vrp/logs/${name}_${i}_${j}.log & 
    done
    sleep 1
done
echo "第三步任务发放完成"
while(true)
do
    echo "-----------------------开始检测-------------------------"
    for((id=0;id<3;id++))
    do
        tasknum=`ssh ${hosts[${id}]} ps aux | grep 'solver.py' | grep 'python' | wc -l` #当前任务数量
	echo "${hosts[${id}]} 执行任务数量为${tasknum} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
	if [ ${tasknum} -eq 0 ]
	then
	    echo "${hosts[${id}]}上的任务执行完成，传回住电脑 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
	    scp -r ${hosts[${id}]}:${out3}/* ${mainhost}:${out3}
	fi 
    done

    filenum=`ssh ${mainhost} ls -l ${out3}|grep "^-"|wc -l`  #统计step3输出文件数量
    tgtfilenum=`expr ${groupnum} \* ${smallgroup}`
    echo "参数${name}下生成的第三步文件数量为：${filenum},目标文件数量为：${tgtfilenum} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
    if [ ${filenum} -eq ${tgtfilenum} ]
    then
	echo "第三步执行完成，准备执行第四步 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
	out4=${root4}/${name}_${i}_${j}
	echo "创建在各个电脑上创建第四步输出文件夹${out4}"
        bash ${allcmd} ${host} mkdir ${out4}
        echo "文件创建完成，开始执行第四步,当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
	python ${step4} ${out2} ${out3} ${out4} ${groupnum} ${smallgroup}
	result=`cat ${out4}/total_cost.txt`
	echo "${name}_${i}_${j}		${result}	`date +'%Y-%m-%d %H:%M:%S'`	${mainhost}" >> /home/jiuxia/vrp/model/result.txt
        break
    fi
    echo "------------------------WAIT--------------------------"
    sleep 300
done
