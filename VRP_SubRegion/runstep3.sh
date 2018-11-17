
#args step3
step3=/home/jiuxia/vrp/model/solver.py
root3=/home/jiuxia/vrp/step3out
root2=/home/jiuxia/vrp/step2out

allcmd=/home/jiuxia/vrp/model/allcmd.sh
host=/home/jiuxia/vrp/model/host.txt

groupnum=$1
smallgroup=$2
instep2=$3    #step2 output
dirname=$4	#step2 dirname
out3=${root3}/${dirname}/result_${groupnum}_${smallgroup}.csv
instep1=${root2}/${dirname}/${groupnum}_${smallgroup}.xlsx
instep2=${root2}/${dirname}/distance_${groupnum}_${smallgroup}.xlsx
#echo "step3 ${step3} ${instep1} ${instep2} ${out3}"
python ${step3} ${instep1} ${instep2} ${out3}

