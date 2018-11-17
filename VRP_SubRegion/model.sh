#shell

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
mainhost=192.168.11.101
hosts=("192.168.11.112" "192.168.11.111" "192.168.11.110" "192.168.11.109" "192.168.11.108" "192.168.11.107" "192.168.11.106" "192.168.11.105" "192.168.11.104" "192.168.11.103" "192.168.11.102" "192.168.11.101");

#step1 args
n_begin=1
n_end=5
k_begin=5
k_end=13
affinity=("euclidean" "l1" "l2" "manhattan" "cosine"); #precomputed
linkage=("complete" "average");

groupstandard=("first_receive_tm" "last_receive_tm");

echo "${#linkage[@]} ${#affinity[@]}"
times=0                         #每轮任务数
pctasknum=1                     #电脑任务数
pcnum=${#hosts[@]}              #电脑数
timethres=11100                  #超出时间阈值，单位s

#task
groupnums=()
smallgroups=()
out2s=()
out3s=()
names=()

#输出发给其他电脑
deliverout(){
    deout=$1
    for((i=0;i<${pcnum};i++))
    do
        scp -r ${mainhost}:${deout}/* ${hosts[i]}:${deout}
    done
}

runstep2(){
    groupnum=$1
    out=$2
    instep1=$3
    for((smallgroup=3;smallgroup<=6;smallgroup++))
    do
        for((gro=0;gro<${#groupstandard[@]};gro++))
        do
            out2=${root2}/${out}_${smallgroup}_${groupstandard[gro]}
            id=`expr ${times} / ${pctasknum}`
	    filenumout2=`ls -l ${out2}|grep "^-"|wc -l`
	    echo "filenumout2=${filenumout2}"
            if [ ${filenumout2} -eq 0 ]
            then
		echo "创建在各个电脑上创建第二步输出文件夹${out2}"
                bash ${allcmd} ${host} mkdir ${out2}
                echo "文件夹创建完成，开始执行第二步，hostid=${hosts[id]} groupnum=${groupnum} smallgroup=${smallgroup} name=${out}_${smallgroup}_${groupstandard[gro]} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                ssh -n ${hosts[id]} nohup bash /home/jiuxia/vrp/model/runstep2.sh ${in} ${out2} ${groupnum} ${smallgroup} ${groupstandard[gro]} ${instep1}
                echo "第二步执行完成，输出传回主电脑，当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                scp -r ${hosts[id]}:${out2}/* ${mainhost}:${out2}
		echo "第二步输出发给其他电脑 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
		deliverout ${out2}
            else
    		echo "第二步已经执行，生成文件数量为${filenumout2},跳过该步开始执行下一步 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
            fi

            out3=${root3}/${out}_${smallgroup}_${groupstandard[gro]}
            filenumout3=`ls -l ${out3}|grep "^-"|wc -l`
	    echo "filenumout3=${filenumout3}"
            if [ ${filenumout3} -eq 0 ]
	    then
		echo "创建在各个电脑上创建第三步输出文件夹${out3}"
                bash ${allcmd} ${host} mkdir ${out3}
                echo "开始并行执行第三步，hostid=${hosts[id]} name=${out}_${smallgroup}_${groupstandard[gro]} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                for((i=0;i<groupnum;i++))
                do
                    for((j=0;j<smallgroup;j++))
                    do
                        echo "hostid=${hosts[id]} name=${out}_${smallgroup}_${groupstandard[gro]}_${i}_${j}"
                        ssh -n ${hosts[id]} nohup bash /home/jiuxia/vrp/model/runstep3.sh ${i} ${j} ${out2} ${out}_${smallgroup}_${groupstandard[gro]} >> /home/jiuxia/vrp/logs/${out}_${smallgroup}_${groupstandard[gro]}_${i}_${j}.log & 
                    done
                    sleep 1
                done
	        echo "第三步任务在${hosts[id]}发放完成，准备下一轮任务 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
            else
                echo "第三步已经执行，生成文件数量为${filenumout3},跳过该步开始执行下一步 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                tgtfilenum=`expr ${groupnum} \* ${smallgroup}`
		if [ ${filenumout3} -eq ${tgtfilenum} ]
                then
         	    echo "参数${out}_${smallgroup}_${groupstandard[gro]}_${groupnum}_${smallgroup}下生成文件数量匹配，准备执行第四步 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    out4=${root4}/${out}_${smallgroup}_${groupstandard[gro]}_${groupnum}_${smallgroup}
		    filenumout4=`ls -l ${out4}|grep "^-"|wc -l`
		    if [ ${filenumout4} -eq 0 ]
        	    then
			echo "创建在各个电脑上创建第四步输出文件夹${out4}"
                        bash ${allcmd} ${host} mkdir ${out4}
                        echo "文件创建完成，开始执行第四步,groupnum=${groupnum} smallgroup=${smallgroup} out=${out4} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                        python ${step4} ${out2} ${out3} ${out4} ${groupnum} ${smallgroup}
                        result=`cat ${out4}/total_cost.txt`
                        echo "${out}_${smallgroup}_${groupstandard[gro]}_${groupnum}_${smallgroup}        ${result}    `date +'%Y-%m-%d %H:%M:%S'`    ${hosts[id2]}" >> /home/jiuxia/vrp/model/result.txt
		    fi
		fi
		echo "continue"
		continue
            fi
            groupnums[${times}]=${groupnum}
            smallgroups[${times}]=${smallgroup}
            out2s[${times}]=${out2}
            out3s[${times}]=${out3}
            names[${times}]=${out}_${smallgroup}_${groupstandard[gro]}_${groupnum}_${smallgroup}
            times=`expr ${times} + 1`
            starttime=`date +%s`
            if [ ${times} -eq ${pcnum} ]
            then
                jdg=(0 0 0 0 0 0 0 0 0 0 0 0)
                while(true)
                do
                    echo "-----------------------开始检测-------------------------"
                    for((id2=0;id2<${pcnum};id2++))
                    do
                    tasknum=`ssh ${hosts[id2]} ps aux | grep 'solver.py' | grep 'python' | wc -l` #当前任务数量
                    echo "${hosts[id2]}执行任务数量为：${tasknum} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    if [ ${tasknum} -eq 0 -a ${jdg[${id2}]} -eq 0 ]
                    then
                        jdg[${id2}]=1
                        end=`expr ${id2} \* ${pctasknum}`
                        end=`expr ${end} + ${pctasknum}`
                        st=`expr ${id2} \* ${pctasknum}`
                        for((start=${st};start<${end};start++))
                        do
                            filenum=`ssh ${hosts[id2]} ls -l ${out3s[${start}]}|grep "^-"|wc -l`  #统计step3输出文件数量
                            tgtfilenum=`expr ${groupnums[${start}]} \* ${smallgroups[${start}]}`
                            echo "参数${names[${start}]}下生成的第三步文件数量为：${filenum},目标文件数量为：${tgtfilenum} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                            if [ ${filenum} -eq ${tgtfilenum} ]
                            then
	    			echo "第三步执行完成，输出传回主电脑，当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
				scp -r ${hosts[id2]}:${out3s[${start}]}/* ${mainhost}:${out3s[${start}]}
		    	        echo "第三步输出发给其他电脑 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                		deliverout ${out3s[${start}]}
                                echo "参数${names[${start}]}下生成文件数量匹配，准备执行第四步 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                                out4=${root4}/${names[${start}]}
                                echo "创建在各个电脑上创建第四步输出文件夹${out4}"
                                bash ${allcmd} ${host} mkdir ${out4}
                                echo "文件创建完成，开始执行第四步,groupnum=${groupnums[${start}]} smallgroup=${smallgroups[${start}]} out=${out4} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                                ssh -n ${hosts[id2]} python ${step4} ${out2s[${start}]} ${out3s[${start}]} ${out4} ${groupnums[${start}]} ${smallgroups[${start}]}
                                result=`ssh -n ${hosts[id2]} cat ${out4}/total_cost.txt`
                                echo "${names[${start}]}	${result}    `date +'%Y-%m-%d %H:%M:%S'`    ${hosts[id2]}" >> /home/jiuxia/vrp/model/result.txt
                                echo "第四步输出从${hosts[id2]}传回主电脑${mainhost}，当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                                scp -r ${hosts[id2]}:${out4}/* ${mainhost}:${out4}
			    else
			        echo "第三步执行完成，但是输出文件不够，跳过第四步，输出传回主电脑，当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                                scp -r ${hosts[id2]}:${out3s[${start}]}/* ${mainhost}:${out3s[${start}]}
				echo "第三步输出发给其他电脑 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                                deliverout ${out3s[${start}]}
				echo "${names[${start}]}       ERROR: filenum=${filenum},tgt=${tgtfilenum}    `date +'%Y-%m-%d %H:%M:%S'`    ${hosts[id2]}" >> /home/jiuxia/vrp/model/result.txt
                            fi
                        done
                    fi
                done
                sumjdg=0
                for((ii=0;ii<${#jdg[@]};ii++)){
                    sumjdg=`expr ${sumjdg} + ${jdg[ii]}`
                }
                echo "当前完成任务电脑数为：${sumjdg} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                if [ ${sumjdg} -eq ${pcnum} ]
                then
                    times=0
		    echo "该轮任务完成，准备发放下一轮任务 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
		    echo "-------------------------WAIT---------------------------"
		    sleep 60
		    echo "开始发放下一轮任务 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    break
                fi
                endtime=`date +%s`
                costtime=`expr ${endtime} - ${starttime}`
                echo "当轮任务消耗时间为：${costtime} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                if [ ${costtime} -gt ${timethres} ]
                then
                    echo "有未输出结果，超时退出！当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    echo "有未输出结果，超时退出！当前时间为`date +'%Y-%m-%d %H:%M:%S'`" >> /home/jiuxia/vrp/model/result.txt
		    times=0
		    echo "该轮任务完成，准备发放下一轮任务 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    echo "-------------------------WAIT---------------------------"
                    sleep 60
                    echo "开始发放下一轮任务 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    break
                fi
                echo "-------------------------WAIT---------------------------"
                sleep 300
            done
        fi
            
        done
    done
}

#step1
for((n=${n_end};n>=${n_begin};n--))
do
    if [ ${n} -eq 1 -o ${n} -eq 4 ]
    then
        for((k=${k_begin};k<=${k_end};k++))
        do
            out=${root}/${n}_${k}
            echo "创建在各个电脑上创建第一步输出文件夹${out}"
            bash ${allcmd} ${host} mkdir ${out}
            echo "文件夹创建完成，开始执行第一步，n=${n} k=${k} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
            python ${step1} ${in} ${out} ${n} ${k} 0 0 0 0 0
            echo "第一步执行完成，将第一步文件发放到其他电脑"
            deliverout ${out}
            groupnum=`cat ${out}/group_num.txt`
            echo "第一步执行完成，开始执行第二步：groupnum=${groupnum} n=${n} k=${k} out=${out} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
            runstep2 ${groupnum} ${n}_${k} ${out}
        done
    elif [ ${n} -eq 2 ];
    then
        for((k=${k_begin};k<=${k_end};k++))
        do
            for((aff=0;aff<${#affinity[@]};aff++))
            do
                for((lin=0;lin<${#linkage[@]};lin++))
                do
                    out=${root}/${n}_${k}_${affinity[aff]}_${linkage[lin]}
                    echo "创建在各个电脑上创建第一步输出文件夹${out}"              
                    bash ${allcmd} ${host} mkdir ${out}
                    echo "文件夹创建完成，开始执行第一步，n=${n} k=${k} affinity=${affinity[aff]} linkage=${linkage[lin]} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    python ${step1} ${in} ${out} ${n} ${k} ${affinity[aff]} ${linkage[lin]} 0 0 0
                    echo "第一步执行完成，将第一步文件发放到其他电脑"
                    deliverout ${out}
                    groupnum=`cat ${out}/group_num.txt`
                    echo "第一步执行完成，开始执行第二步：groupnum=${groupnum} n=${n} k=${k} affinity=${affinity[aff]} linkage=${linkage[lin]} out=${out} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    runstep2 ${groupnum} ${n}_${k}_${affinity[aff]}_${linkage[lin]} ${out}
                done
            done
        done
    elif [ ${n} -eq 3 ];
    then
        for((k=${k_begin};k<=${k_end};k++))
        do
	    threshold=0.05
            for((;$(echo "(${threshold}) <= (0.2)" | bc);))
            do
                for((branching_factor=10;branching_factor<=50;branching_factor=`expr ${branching_factor} + 10`))
                do
                    out=${root}/${n}_${k}_${threshold}_${branching_factor}
                    echo "创建在各个电脑上创建第一步输出文件夹${out}"   
                    bash ${allcmd} ${host} mkdir ${out}
                    echo "文件夹创建完成，开始执行第一步，n=${n} k=${k} threshold=${threshold} branching_factor=${branching_factor} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    python ${step1} ${in} ${out} ${n} ${k} 0 0 ${threshold} ${branching_factor} 0
                    echo "第一步执行完成，将第一步文件发放到其他电脑"
                    deliverout ${out}
                    groupnum=`cat ${out}/group_num.txt`
                    echo "第一步执行完成，开始执行第二步：groupnum=${groupnum} n=${n} k=${k} threshold=${threshold} branching_factor=${branching_factor} out=${out} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    runstep2 ${groupnum} ${n}_${k}_${threshold}_${branching_factor} ${out}
                done
	        threshold=$((echo "${threshold}+ (0.04)")|bc|awk '{printf "%f",$0}')
            done
        done
    elif [ ${n} -eq 5 ];
    then
        m1=-0.5
        for((;$(echo "(${m1}) <= (-0.35)" | bc);))
        do
	    echo "m1=${m1}"
	    m2=-0.8
            for((;$(echo "(${m2}) <= (-0.7)" | bc);))
            do
		m3=-1.5
                for((;$(echo "(${m3}) <= (-1.2)" | bc);))
                do
                    out=${root}/${n}_${m1}_${m2}_${m3}
                    echo "创建在各个电脑上创建第一步输出文件夹${out}"   
                    bash ${allcmd} ${host} mkdir ${out}
                    echo "文件夹创建完成，开始执行第一步，n=${n} slope=${m1},${m2},${m3} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    python ${step1} ${in} ${out} ${n} 0 0 0 0 0 ${m1},${m2},${m3}
                    echo "第一步执行完成，将第一步文件发放到其他电脑"
                    deliverout ${out}
                    groupnum=`cat ${out}/group_num.txt`
                    echo "第一步执行完成，开始执行第二步：groupnum=${groupnum} slope=${m1},${m2},${m3} out=${out} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                    runstep2 ${groupnum} ${n}_${m1}_${m2}_${m3} ${out}
		    m3=$((echo "${m3}+ (0.05)")|bc|awk '{printf "%f",$0}')
                done
		m2=$((echo "${m2}+ (0.03)")|bc|awk '{printf "%f",$0}')
            done
            m1=$((echo "${m1}+ (0.03)")|bc|awk '{printf "%f",$0}')
        done
        
	m1=-0.4
        for((;$(echo "(${m1}) <= (-0.3)" | bc);))
        do
	    m2=-0.65
            for((;$(echo "(${m2}) <= (-0.55)" | bc);))
            do
		m3=-1
                for((;$(echo "(${m3}) <= (-0.85)" | bc);))
                do
		    m4=-2
                    for((;$(echo "(${m4}) <= (-1.5)" | bc);))
                    do
                        out=${root}/${n}_${m1}_${m2}_${m3}_${m4}
                        echo "创建在各个电脑上创建第一步输出文件夹${out}"   
                        bash ${allcmd} ${host} mkdir ${out}
                        echo "文件夹创建完成，开始执行第一步，n=${n} slope=${m1},${m2},${m3},${m4} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                        python ${step1} ${in} ${out} ${n} 0 0 0 0 0 ${m1},${m2},${m3},${m4}
                        echo "第一步执行完成，将第一步文件发放到其他电脑"
                        deliverout ${out}
                        groupnum=`cat ${out}/group_num.txt`
                        echo "第一步执行完成，开始执行第二步：groupnum=${groupnum} slope=${m1},${m2},${m3},${m4} out=${out} 当前时间为`date +'%Y-%m-%d %H:%M:%S'`"
                        runstep2 ${groupnum} ${n}_${m1}_${m2}_${m3}_${m4} ${out}
			m4=$((echo "${m4}+ (0.03)")|bc|awk '{printf "%f",$0}')
                    done
    		    m3=$((echo "${m3}+ (0.03)")|bc|awk '{printf "%f",$0}')
                done
		m2=$((echo "${m2}+ (0.03)")|bc|awk '{printf "%f",$0}')
            done
            m1=$((echo "${m1}+ (0.03)")|bc|awk '{printf "%f",$0}')
        done
    fi
done
