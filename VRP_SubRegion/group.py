# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 11:08:48 2018

@author: jiuxia
"""

import sys
import pandas as pd

input=sys.argv[1]
out=sys.argv[2]
Group_num = int(sys.argv[3])
small_group = int(sys.argv[4])   ## 2-6
group_standard = sys.argv[5]    #'first_recieve_tm'
instep1=sys.argv[6]

distance = pd.read_table(input+'/input_distance_time.txt',sep = ',')

for j in range(Group_num):
    c1_m_title = instep1+'/c_' + str(j) +'.xlsx'
    data_title = instep1+'/'+str(j) +'.xlsx'
    data = pd.read_excel(data_title)
    c1_m = pd.read_excel(c1_m_title)
    #print(data.head())
    
    for i in range(small_group):
        group_name='c'+str(i)
        locals()[group_name] = []

    for name,group in data.groupby(group_standard):
        if len(group)%small_group == 0:
            s = len(group)/small_group
        else:
            s = int(float(len(group))/small_group)+1    
        ID = list(group['ID'])
        for i in range(small_group):
            group_name='c'+str(i)
            if i != small_group-1:
                locals()[group_name] = locals()[group_name] +ID[int(i*s):int((i+1)*s)]
            else:
                locals()[group_name] =  locals()[group_name] + ID[int(i*s):]
 
    for i in range(small_group):
        group_name='c'+str(i)
        #print(locals()[group_name])

        final_name = 'c' + str(i) +'df'
        locals()[final_name] = c1_m
        #print(locals()[final_name])
        
    for row in data.index:
        for i in range(small_group):
            group_name='c'+str(i)
            final_name = 'c' + str(i) +'df'
            if data.loc[row,'ID'] in locals()[group_name]:
                locals()[final_name] = locals()[final_name].append(data.ix[row])
                
    for i in range(small_group):
        title = out+'/'+str(j) +'_' +str(i) +'.xlsx'
        final_name = 'c' + str(i) +'df'
        locals()[final_name].to_excel(title)
        
        d_1 = pd.merge(locals()[final_name],distance,how = 'inner',left_on = 'ID', right_on = 'from_node')
        d_2 = pd.merge(locals()[final_name],d_1,how = 'inner',left_on = 'ID',right_on = 'to_node')
        d_2 = d_2[['from_node','to_node','distance','spend_tm']]        

        d_2_title = out+'/distance_' +str(j)+'_'+str(i)+'.xlsx'
        d_2.to_excel(d_2_title)
