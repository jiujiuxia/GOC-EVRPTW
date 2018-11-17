# -*- coding: utf-8 -*-
"""
Created on Sun Jul 08 16:21:21 2018

@author: jiuxia
"""

import sys
import pandas as pd

instep2=sys.argv[1]
instep3=sys.argv[2]
out=sys.argv[3]
Group_num=int(sys.argv[4])
cla=int(sys.argv[5])

d = []
final_data = pd.DataFrame()
#Group_num = 8
#cla = 5

for c in range(Group_num):    
    for i in range(cla):
        data1_title = instep2+'/'+str(c) +'_'+str(i)+'.xlsx'
        dist_title = instep2+'/distance_' +str(c) +'_' +str(i) +'.xlsx'
        data1 = pd.read_excel(data1_title)
        dist = pd.read_excel(dist_title)
        node = list(data1['ID'])
        data1.set_index(["ID"], inplace=True)
        
        s = len(data1[data1['type'] == 3])        #共4个充电桩

        ReaTime = {}
        DueTime = {}
        Distance = {}
        Time = {}
        
        for n in node:
            ReaTime[n] = data1.loc[n,'first_receive_tm']
            DueTime[n] = data1.loc[n,'last_receive_tm']
        #距离和时间
        node.append(2000)
        for n in dist.index:
            Distance[dist.loc[n,'from_node'],dist.loc[n,'to_node']] = dist.loc[n,'distance']
            Time[dist.loc[n,'from_node'],dist.loc[n,'to_node']] = dist.loc[n,'spend_tm']
        ##回来的点
        for n in node:
            if n not in [0,2000]:
                Distance[2000,n] = Distance[0,n]
                Distance[n,2000] = Distance[n,0]
                Time[n,2000] = Time[n,0]
                Time[2000,n] = Time[0,n]
        Distance[0,2000] = Distance[2000,0] = 0
        Time[0,2000] = Time[2000,0] = 0
        
        ReaTime[2000] = ReaTime[0]
        DueTime[2000] = DueTime[0]
        #print('data ok')
        
        result_title = instep3+'/result_' +str(c) +'_' +str(i) +'.csv'
        #print(result_title)
        data = pd.read_csv(result_title)
        
        for j in data.index:
            trans_code = 'DP' +str(len(final_data)+1).zfill(4)    #编码
            #print(trans_code)       
            vehicle_type = data.loc[j,'车型']
            dist_seq = data.loc[j,'经过的点'].replace(',',';').replace(' ','')
            dist_seq = dist_seq[1:len(dist_seq)-1]
            dist_seq = dist_seq + ';0'                           #路线
            
            points = dist_seq.split(';')            
            for p in range(len(points)):
                points[p] = int(points[p])
            #print(points)
                
            now = int(data.loc[j,'出发时间'])
            pre_time = 0
            
            d = d+ points[1:len(points)-1]
            
            for p in range(len(points)-2):
                now = now + Time[points[p],points[p+1]]
                if now < int(ReaTime[points[p+1]]):
                    pre_time = pre_time+(int(ReaTime[points[p+1]])-now) #等待时间
                    now = int(ReaTime[points[p+1]]) +30
                elif now >int(DueTime[points[p+1]]):
                    print(points[p],'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                else:
                    now = now +30  
                    
            end_time = now + Time[points[len(points)-2],2000]   #结束时间min

            distance = 0            
            for p in range(len(points)-1):
                distance = distance + Distance[points[p],points[p+1]]
                    
            lea_hour = int(data.loc[j,'出发时间'])/60
            lea_minute = int(data.loc[j,'出发时间'])%60      
            distribute_lea_tm = str(8+int(lea_hour)).zfill(2) +':'+str(int(lea_minute)).zfill(2) #出发时间
            arr_hour = end_time/60
            arr_minute = end_time%60      
            distribute_arr_tm = str(8+int(arr_hour)).zfill(2) +':'+str(int(arr_minute)).zfill(2) #结束时间  
            '''
            if vehicle_type == 1:
                if distance>100000 and data.loc[j,'充电次数'] == 0:
                    print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',distance,distance1)
                if distance >100000 and data.loc[j,'充电次数'] == 1:
                    print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD!!!!!!!!!!!!!!!',distance,distance1)
            if vehicle_type ==2:
                if distance >120000 and data.loc[j,'充电次数'] == 0:
                    print('d@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',distance,distance1)
                if distance >=240000 and data.loc[j,'充电次数'] != 2:
                    print('ddd@@@@@@@!!!!!!!!!!!!!!!!!!!!!!!!!!!1!!!!!!!!!!',distance,distance1)
            '''        
            cost = [0.012,0.014]
            fix_cost = [200,300]
            
            trans_cost = round(distance*cost[vehicle_type-1],2)        #运输费用
            charge_cost = data.loc[j,'充电次数']*50.0                  #充电费用
            wait_cost = round(pre_time*0.4,2)                          #等待费用
            fixed_use_cost = fix_cost[vehicle_type-1]                  #固定成本
            total_cost = round(trans_cost+charge_cost+wait_cost+fixed_use_cost,2)  #总成本
            charge_cnt = data.loc[j,'充电次数']                          #充电次数
            each = [trans_code,vehicle_type,dist_seq, distribute_lea_tm,distribute_arr_tm,distance,trans_cost,charge_cost,wait_cost,fixed_use_cost,total_cost,charge_cnt]
            final_data = final_data.append([each]) 
final_data.columns = ['trans_code','vehicle_type','dist_seq','distribute_lea_tm','distribute_arr_tm','distance','trans_cost','charge_cost','wait_cost','fixed_use_cost','total_cost','charge_cnt']
final_data.set_index(["trans_code"], inplace=True)
print(final_data.head())
final_data.to_csv(out+'/Result.csv')    

final_cost = final_data['total_cost'].sum()

file=open(out+'/total_cost.txt','w')
file.write(str(final_cost))
file.close()

print('final cost=',final_cost)

d.sort()
#for i in d:
    #if d.count(i)>1:
        #print(i)
da = pd.DataFrame()
da = da.append([d])
#da.to_excel('exame.xlsx')        
        
            
        
