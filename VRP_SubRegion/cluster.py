# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 16:09:54 2018

@author: jiuxia
"""

import sys
import pandas as pd
import random
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import Birch

input=sys.argv[1]
out=sys.argv[2]
n=int(sys.argv[3])
k=int(sys.argv[4])
affinity=sys.argv[5]
linkage=sys.argv[6]
threshold=float(sys.argv[7])
branching_factor=int(sys.argv[8])
inslope=sys.argv[9]
if len(sys.argv) == 10:
    slope=[float(x) for x in inslope.split(',',-1)]
print(len(sys.argv))
print(slope)

data = pd.read_excel(input+'/input_node.xlsx')
m = pd.read_excel(input+'/m.xlsx')

#聚类特征选择
feature = ['lng','lat'] ###('载重和时间')
Data_for_Cluster = data[feature]

def k_means(data,Data_for_Cluster,k):
    #k_means的参数选择
    #k = 2   #（4-15）
    print('k_means','聚类数：',k)
    kmmod = KMeans(n_clusters=k)
    pred = kmmod.fit_predict(Data_for_Cluster)
    for i in data.index:
        data.loc[i,'clustering'] = pred[i]
    return data

def agg(data,Data_for_Cluster,k,affinity,linkage):
    #层次聚类的参数选择
    #k = 2
    #affinity = 'euclidean'   #(’euclidean’，’l1’，’l2’，’mantattan’，’cosine’，’precomputed’)
    #linkage = 'complete'     #('complete','average')
    print('agg','聚类数：',k,'affinity:',affinity,'linkage：',linkage)
    aggmod = AgglomerativeClustering(n_clusters=k, affinity=affinity,linkage=linkage)
    pred = aggmod.fit_predict(Data_for_Cluster)
    for i in data.index:
        data.loc[i,'clustering'] = pred[i]
    return data

def Bir(data,Data_for_Cluster,k,threshold,branching_factor):   
    #Birch聚类的参数选择
    #k = 2  #[4-15,None]
    #threshold = 0.5  #[0.5,0.3,0.1]
    #branching_factor= 50 #[50,20,10]
    print('Bir','聚类数：',k,'threshold：',threshold,'branching_factor:',branching_factor)
    Birmod = Birch(n_clusters = k,threshold=threshold,branching_factor=branching_factor)
    pred = Birmod.fit_predict(Data_for_Cluster)
    for i in data.index:
        data.loc[i,'clustering'] = pred[i]
    return data

def lng(data,k):
    #直接径向划分
    #k = 8
    print('lng','聚类数：',k)
    cluster_name = range(k)
    max_lng = data['lng'].max()
    min_lng = data['lng'].min()
    sep_lng = []
    while True:
        value = random.uniform(min_lng, max_lng)
        if value not in sep_lng:
            sep_lng.append(value)#随机数范围
        if len(sep_lng)==k:
            break
    sep_lng.sort()    
    for i in range(len(sep_lng)):
        print(i)
        if i == 0:
            print(sep_lng[i])
            for j in data.index:
                if data.loc[j,'lng']<=sep_lng[i]:
                    data.loc[j,'clustering']= cluster_name[i]
        else:
            print(sep_lng[i])
            for j in data.index:
                if data.loc[j,'lng']>sep_lng[i-1] and data.loc[j,'lng']<=sep_lng[i]:
                    data.loc[j,'clustering'] = cluster_name[i]
    
    for j in data.index:
        if data.loc[j,'lng']>sep_lng[len(sep_lng)-1]:
            data.loc[j,'clustering'] = cluster_name[len(cluster_name)-1]
    return data

def std_lng(lng):
    lng = lng-116.571614
    return lng

def std_lat(lat):
    lat = lat-39.792844
    return lat

def line(data,slope):
    data['lng'] = data['lng'].apply(std_lng)
    data['lat'] = data['lat'].apply(std_lat)
    k = len(slope)+3
    print('聚类数：',k)
    cluster_name = range(k)
    for i in range(len(slope)):
        if i ==0:
            for j in data.index:
                if data.loc[j,'lng']<0 and data.loc[j,'lat']>0:
                    if float(data.loc[j,'lat'])/float(data.loc[j,'lng']) >= slope[i]:
                        data.loc[j,'clustering'] = cluster_name[i]
        else:
            for j in data.index:
                if data.loc[j,'lng']<0 and data.loc[j,'lat']>0:
                    if float(data.loc[j,'lat'])/float(data.loc[j,'lng'])>=slope[i] and float(data.loc[j,'lat'])/float(data.loc[j,'lng'])<slope[i-1]:
                        data.loc[j,'clustering'] = cluster_name[i]
    for j in data.index:
        if data.loc[j,'lng']<0 and data.loc[j,'lat']>0:
            if float(data.loc[j,'lat'])/float(data.loc[j,'lng'])<slope[len(slope)-1]:
                data.loc[j,'clustering'] = cluster_name[len(cluster_name)-3]
        if data.loc[j,'lng']>=0 and data.loc[j,'lat']>0:
            data.loc[j,'clustering'] = cluster_name[len(cluster_name)-2]
        if data.loc[j,'lat']<=0:
            data.loc[j,'clustering'] = cluster_name[len(cluster_name)-1]
    return data

def group(data,m):
    Group_num = 0
    data['last_receive_tm'] = data['last_receive_tm'].map(int)
    data['first_receive_tm'] = data['first_receive_tm'].map(int)
    for name,group in data.groupby('clustering'):
        Group_num = Group_num +1
        c_m = m
        c_m = c_m.append(group[group['type'] == 3])   ##充电站和配送中心
        c = group[group['type'] == 2]
        title1 = out+'/c_' + str(int(name)) +'.xlsx'
        title2 = out+'/'+str(int(name)) +'.xlsx'
        c_m.to_excel(title1)
        c.to_excel(title2)
    return Group_num


# n = 3    #1-4
# k = 8     #4-15
# affinity = 'euclidean'   # #(’euclidean’，’l1’，’l2’，’mantattan’，’cosine’，’precomputed’)
# linkage = 'complete'     # #('complete','average')
# threshold = 0.08          # #[0.2,0.1,0.05]
# branching_factor= 30     # #[50,20,10]

if n == 1:
    data = k_means(data,Data_for_Cluster,k)
if n == 2:
    data = agg(data,Data_for_Cluster,k,affinity,linkage)
if n == 3:
    data = Bir(data,Data_for_Cluster,k,threshold,branching_factor)
if n == 4:
    data = lng(data,k)
if n == 5:
    data = line(data,slope)
    
data.to_excel(out+'/cluster.xlsx')
Group_num = group(data,m)    

file=open(out+'/group_num.txt','w')
file.write(str(Group_num))
file.close()

