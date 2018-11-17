# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 11:23:02 2018

@author: jiuxia
"""

import sys
import pandas as pd
from gurobipy import *
import time

start_code = time.time()

input1=sys.argv[1]
input2=sys.argv[2]
out=sys.argv[3]

data = pd.read_excel(input1)
dist = pd.read_excel(input2)
node = list(data['ID'])
data.set_index(["ID"], inplace=True)

s = len(data[data['type'] == 3])        #共4个充电桩
print(s)

#电动车状态
Battery = 120000.0
Capacity = 2.5
Volume = 16
Consume = 1.0
SwapTime = 30.0

Demand = {}
Vol_Demand = {}
ReaTime = {}
DueTime = {}
SerTime = 30.0
Distance = {}
Time = {}

for i in node:
    Demand[i] = data.loc[i,'pack_total_weight']
    Vol_Demand[i] = data.loc[i,'pack_total_volume']
    ReaTime[i] = int(data.loc[i,'first_receive_tm'])
    DueTime[i] = int(data.loc[i,'last_receive_tm'])
#距离和时间
node.append(2000)
for i in dist.index:
    Distance[dist.loc[i,'from_node'],dist.loc[i,'to_node']] = dist.loc[i,'distance']
    Time[dist.loc[i,'from_node'],dist.loc[i,'to_node']] = dist.loc[i,'spend_tm']
##回来的点
for i in node:
    if i not in [0,2000]:
        Distance[2000,i] = Distance[0,i]
        Distance[i,2000] = Distance[i,0]
        Time[i,2000] = Time[i,0]
        Time[2000,i] = Time[0,i]
Distance[0,2000] = Distance[2000,0] = 0
Time[0,2000] = Time[2000,0] = 0

Demand[2000] = Demand[0]
Vol_Demand[2000] = Vol_Demand[0]
ReaTime[2000] = ReaTime[0]
DueTime[2000] = DueTime[0]
n = len(node)
print(node)
print('data ok')

m = Model('VRP')
m.setParam('OutputFlag',True)########
m.setParam('TimeLimit',43200.0)

###构造变量
#travle or not
x = {}           
for i in node:
    for j in node:
        if i != j:
            x[i,j] = m.addVar(0.0, 1.0, 0.0, GRB.BINARY,'x_%s%s' % (i, j))
#到达时间
ArrTime = {}
for i in node:
    ArrTime[i] = m.addVar(ReaTime[i], DueTime[i], 0.0, GRB.CONTINUOUS, "ArrTime_%s" %i)
#剩余货物
RemainCargo = {}
RemainVelocity = {}
for i in node:
    RemainCargo[i] = m.addVar(0,Capacity,0.0,GRB.CONTINUOUS,'RemainCargo_%s' %i)
for i in node:
    RemainVelocity[i] = m.addVar(0,Volume,0.0,GRB.CONTINUOUS,'RemainVelocity_%s' %i)
#剩余电量
RemainBattery = {}
for i in node:
    RemainBattery[i] = m.addVar(0,Battery, 0.0, GRB.CONTINUOUS,'RemainBattery_%s' %i)
#Integrate new variables
    m.update()

#构造目标函数
obj1 = quicksum(x[0,j] for j in node[1:n]) #车辆数
obj2 = quicksum(Distance[i,j]*x[i,j] for i in node for j in node[1:n] if i != j)  #运输距离
obj3 = quicksum(x[i,j] for i in node[1:s+1] for j in node[s+1:n])      #充电次数

m.setObjective(50*obj3 + 0.014*obj2 + 300*obj1,GRB.MINIMIZE)

##构造约束条件
#1.每个顾客点都被访问
for i in node[s+1:n-1]:
    m.addConstr(quicksum(x[i,j] for j in node[1:n] if i != j) == 1) 

#2.虚拟充电站访问设置
for i in node[1:s+1]:
    m.addConstr(quicksum(x[i,j] for j in node[1:n] if i != j) <= 5) 

#3.从A点进入了就要从A点出去
for h in node[1:n-1]:
    m.addConstr(quicksum(x[h,i] for i in node[1:n] if i != h) - quicksum(x[j,h] for j in node[0:n-1] if h != j) == 0)

#4.时间窗
for j in node[1:n]:
    m.addConstr(ArrTime[0]+(Time[0,j]+0)*x[0,j]-DueTime[0]*(1-x[0,j])-ArrTime[j]<=0)
for i in node[s+1:n-1]:
    for j in node[1:n]:
        if i != j:
            m.addConstr(ArrTime[i]+(Time[i,j]+SerTime)*x[i,j]-DueTime[0]*(1-x[i,j])-ArrTime[j]<=0)
for i in node[1:s+1]:
    for j in node[1:n]:
        if i != j:
            m.addConstr(ArrTime[i]+(Time[i,j]+SwapTime)*x[i,j]-(DueTime[0]+SwapTime)*(1-x[i,j])-ArrTime[j]<=0)

#5.容量限制
for i in node[0:n-1]:
    for j in node[1:n]:
        if i != j:
            m.addConstr(RemainCargo[j]-RemainCargo[i]+Demand[i]*x[i,j]-Capacity*(1-x[i,j])<=0)
for i in node[0:n-1]:
    for j in node[1:n]:
        if i != j:
            m.addConstr(RemainVelocity[j]-RemainVelocity[i]+Vol_Demand[i]*x[i,j]-Volume*(1-x[i,j])<=0)

#6.电池容量限制
for i in node[s+1:n-1]:
    for j in node[1:n]:
        if i != j:
            m.addConstr(RemainBattery[j]-RemainBattery[i]+Consume*Distance[i,j]*x[i,j]-Battery*(1-x[i,j])<=0)
for j in node[1:n]:
    m.addConstr(RemainBattery[j]-RemainBattery[0]+Consume*Distance[0,j]*x[0,j]-Battery*(1-x[0,j])<=0)

for i in node[1:s+1]:
    for j in node[1:len(node)]:
        if i != j:
            m.addConstr(RemainBattery[j] +Consume*Distance[i,j]*x[i,j]-Battery<=0)            

#7.其他的一些限制
for i in node[1:n-1]:
    m.addConstr(x[i,0] == 0)
    m.addConstr(x[2000,i] == 0)

#m.addConstr(x[0,node[1]] == 0)
#m.addConstr(x[node[1],2000] == 0)

m.update()

try:
    m.optimize()
    print(m.ObjVal)
except GurobiError:
    print('Error reported')
print("optimize()")
print(GRB.Status)

def printTour(solution, route, start, distance, demand,vol_demand,sol_time,solved_point,point):
    route = route + str(start) + ' -> '
    if start not in node[0:s+1]:
        solved_point.append(start)
    point.append(start)
    demand += Demand[start]
    vol_demand +=Vol_Demand[start]
    for i in node:
        if start != i:
            if (solution[start, i]> 0.5) :
                if i not in solved_point and (round(sol_time[i])>=round(sol_time[start]+30+Time[start,i])): 
                    totalDistance = distance + Distance[start,i]
                    if (i == 2000):
                        return [
                        totalDistance,
                        demand,
                        vol_demand,
                        route + '2000',
                        start,        #最后一个点
                        point,
                        solved_point
                        ]
                    return printTour(solution, route, i, totalDistance, demand,vol_demand,sol_time,solved_point,point)         
    
E = pd.DataFrame()
if True:
    print('objective: %f' % m.ObjVal)
    solution = m.getAttr('x', x)
    sol_time = m.getAttr("x", ArrTime)

    solved_point = []
    for i in node:
        if i != 0:
            if solution[0,i] >0.5:
                start_time = sol_time[i]-Time[0,i]
                output = printTour(solution,'0 ->',i,Distance[0,i],0,0,sol_time,solved_point,[0])
                solved_point = output[6]                
                points = output[5]
                charge_time = 0
                for p in points:
                    if p in node[1:s+1]:
                        charge_time = charge_time+1
                output = output[0:6] +[start_time,charge_time]  
                if output[0]<=100000 and output[1]<=2 and output[2]<=12:
                    output.append(1)
                else:
                    output.append(2)
                E = E.append([output])

    E.columns= [u'里程',u'总重量',u'总体积',u'顺序',u'最后一点',u'经过的点',u'出发时间',u'充电次数',u'车型']  
    E.to_csv(out,encoding = 'utf-8')
    
end_code = time.time()
print(start_code-end_code)

