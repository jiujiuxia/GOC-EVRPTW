mainhost=192.168.12.113
hosts=("192.168.12.116" "192.168.12.115" "192.168.12.113");
#hosts=("192.168.11.112" "192.168.11.111" "192.168.11.110" "192.168.11.109" "192.168.11.108" "192.168.11.107" "192.168.11.106" "192.168.11.105" "192.168.11.104" "192.168.11.103" "192.168.11.102" "192.168.11.101");

for((i=0;i<${#hosts[@]};i++))
do
    #scp -r ${mainhost}:/home/jiuxia/vrp/step2out/* ${hosts[i]}:/home/jiuxia/vrp/step2out
    #scp -r ${mainhost}:/home/jiuxia/vrp/step3out/* ${hosts[i]}:/home/jiuxia/vrp/step3out
    scp -r ${mainhost}:/home/jiuxia/vrp/model/* ${hosts[i]}:/home/jiuxia/vrp/model
    #scp -r ${hosts[i]}:/home/jiuxia/vrp/step3out/* ${mainhost}:/home/jiuxia/vrp/step3out
done

