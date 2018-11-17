# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 23:24:28 2018

@author: jiuxia
"""

import random, math, sys
import matplotlib.pyplot as plt # 
from copy import deepcopy
import copy
import pandas as pd

data = pd.DataFrame()
result = pd.DataFrame()
distance = pd.read_table('input_distance_time.txt',sep = ',')

for c in [0]:    
    for i in range(3):
        data1_title = str(c) +'_'+str(i)+'.xlsx'
        result_title = 'result_' + str(c) +'_' +str(i) + '.csv'
        data1 = pd.read_excel(data1_title)
        result1 = pd.read_csv(result_title)
        data = data.append(data1)
        result = result.append(result1)

data.set_index(['ID'],inplace = True)

station = []
for i in data.index:
    if i>1000 and i not in station:
        station.append(i)
print(station)       

result = result['经过的点']
result = pd.Series.to_frame(result)
node =[]
station_used = []
for i in range(len(result)):
    each = result.iloc[i,0]
    each = each[1:len(each)-1]
    each = each.split(',')
    each = [int(x) for x in each]
    node.append(each)
print(node)
for i in range(len(node)):
    for j in range(len(node[i])):
        if node[i][j]>1000:
            station_used.append(node[i][j])
            if station_used.count(node[i][j])>1:
                for s in station:
                    if s not in station_used:
                        station_used[len(station_used)-1] = s
                        node[i][j] = s
                        break


cus_data = data[data['type']==2]
Node = [0] +list(cus_data.index) + station_used    
all_Node = [0] +list(cus_data.index) + station

print(Node)
final_data = pd.DataFrame()
final_all_data = pd.DataFrame()

for i in Node:
    final_data = final_data.append(data.ix[i])
final_data.drop_duplicates(subset=None, keep='first', inplace=True)

for i in all_Node:
    final_all_data = final_all_data.append(data.ix[i])
final_all_data.drop_duplicates(subset=None, keep='first', inplace=True)

d_1 = pd.merge(final_all_data,distance,how = 'inner',left_on = 'ID', right_on = 'from_node')
d_2 = pd.merge(final_all_data,d_1,how = 'inner',left_on = 'ID',right_on = 'to_node')
d_2 = d_2[['from_node','to_node','distance','spend_tm']]  


test_data = final_all_data
test_dist = d_2


DEBUG = False
initial = []
l = []
for i in range(29):
    l.append(i)

for i in Node:
    each = []
    random.shuffle(l)
    for j in l:
        each = each+node[j]
    each.append(0)
    initial.append(each)

geneNum =200  # 种群数量
generationNum = 1000 # 迭代次数

CENTER = 0  # 配送中心

HUGE = 999999999999
VARY = 0.5  # 变异几率

n = len(test_data[test_data['type'] == 2])  # 客户点数量
print(n)
m = len(test_data[test_data['type'] == 3])  # 换电站数量
k =999  # 车辆数量
Q = 2.5  # 额定载重量, t
Q_V = 16.0
dis = 120000  # 续航里程, m
costPerKilo = 0.014  # 油价
epu = 0.04  # 早到惩罚成本
lpu = 999999999999  # 晚到惩罚成本

X = {}
Y = {}
t_w ={}
t_v ={}
eh = {}
lh = {}
h = {}
Distance = {}
Time = {}


for i in all_Node:
    #坐标
    X[i] = test_data.loc[i,'lng']
    Y[i] = test_data.loc[i,'lat']
    #需求量
    t_w[i] = test_data.loc[i,'pack_total_weight']
    t_v[i] = test_data.loc[i,'pack_total_volume']
    #时间窗
    eh[i] = int(test_data.loc[i,'first_receive_tm'])
    lh[i] = int(test_data.loc[i,'last_receive_tm'])
    
    Distance[i,i] = 0
    Time[i,i] = 0
    #服务时间
    h[i] = 30
h[0] = 0

    

#距离和时间
for i in test_dist.index:
    Distance[test_dist.loc[i,'from_node'],test_dist.loc[i,'to_node']] = test_dist.loc[i,'distance']
    Time[test_dist.loc[i,'from_node'],test_dist.loc[i,'to_node']] = test_dist.loc[i,'spend_tm']
Node = Node[1:]

class Gene:
    def __init__(self, name = 'gene', node = None, null = False):
        self.name = name
        self.length = n + m + 1
        if null == True:        
            self.data = self._getGene(node)
        else:
            assert(self.length+k >= len(node))
            self.data = node
        self.fit = self.getFit()
        self.chooseProb = 0  # 选择概率

    # randomly choose a gene
    def _generate(self,node):
        #print(node)
        random.shuffle(node)
        node.insert(0, CENTER)
        node.append(CENTER)
        #print('generate',node)
        return node

    # insert zeors at proper positions
    def _insertZeros(self, data):
        sum_w = 0
        sum_v = 0
        newData = []
        for point in data:
            sum_w += t_w[point]
            sum_v += t_v[point]
            if sum_w > Q or sum_v > Q_V:
                newData.append(CENTER)
                #print(sum_w,sum_v)
                #print(newData)
                sum_w = t_w[point]
                sum_v = t_v[point]
            newData.append(point)
        return newData

    # return a random gene with proper center assigned
    def _getGene(self, node):
        data = self._generate(node)
        data = self._insertZeros(data)
        return data

    # return fitness
    def getFit(self):
        fit = distCost = timeCost = overloadCost = overloadCost_V =  fuelCost = fixCost  = 0
        dist = []  # from this to next
        # calculate distance
        i = 0
        while i < len(self.data)-1:
            dist.append(Distance[self.data[i],self.data[i+1]])
            i += 1
        # distance cost
        distCost = sum(dist)*costPerKilo
        
        # time cost
        timeSpent = 0
        for i in range(len(self.data)-1):
            # new car
            if self.data[i] == CENTER:
                timeSpent = 0
            # update time spent on road
            timeSpent += Time[self.data[i],self.data[i+1]]
            # arrive early
            if timeSpent < eh[self.data[i+1]]:
                timeCost += ((eh[self.data[i+1]] - timeSpent) * epu)
                timeSpent = eh[self.data[i+1]]
            # arrive late
            elif timeSpent > lh[self.data[i+1]]:
                timeCost += ((timeSpent - lh[self.data[i+1]]) * lpu)
            # update time
            timeSpent += h[self.data[i+1]]        
        
        '''
        # time cost
        timeCostTotal = 0
        for i in range(len(self.data)-1):
            print(i,self.data)
            # new car
            if self.data[i] == CENTER:
                start_time = eh[self.data[i+1]]-Time[self.data[i],self.data[i+1]]
                end_time   = lh[self.data[i+1]]-Time[self.data[i],self.data[i+1]]
                print(range(start_time,end_time,10))
                eachcost = []
                for j in range(start_time,end_time,10):
                    print(j)
                    p = i
                    timeSpent = j
                    while True:
                        print(p)
                        # update time spent on road
                        timeSpent += Time[self.data[p],self.data[p+1]]
                        # arrive early
                        if timeSpent < eh[self.data[p+1]]:
                            if self.data[p] != CENTER:
                                timeCost += ((eh[self.data[p+1]] - timeSpent) * epu)
                            timeSpent = eh[self.data[p+1]]
                        # arrive late
                        elif timeSpent > lh[self.data[p+1]]:
                            timeCost += ((timeSpent - lh[self.data[p+1]]) * lpu)
                        # update time
                        timeSpent += h[self.data[p+1]]
                        p = p+1
                        if self.data[p] == CENTER:
                            break
                    print(j,timeCost)
                    eachcost.append(timeCost)
            timeCostTotal.append(min(eachcost))
        '''           
        # overload cost and out of fuel cost
        load_w = 0
        load_v = 0 
        distAfterCharge = 0
        for i in range(len(self.data)-1):

            # charge here
            if self.data[i] > 1000:
                distAfterCharge = 0
            # at center, re-load
            elif self.data[i]== CENTER:
                load_w = 0
                load_v = 0
                distAfterCharge = dist[i]
            # normal
            else:
                load_w += t_w[self.data[i]]
                load_v += t_v[self.data[i]]
                distAfterCharge += dist[i]
                # update load and out of fuel cost
                overloadCost += (HUGE * (load_w > Q))
                overloadCost_V += (HUGE * (load_v > Q_V))
                fuelCost += (HUGE * (distAfterCharge > dis))
        
        car_num = self.data.count(0)-1
        fixCost = car_num*300
        fit = distCost + timeCost + overloadCost + fuelCost + fixCost + overloadCost_V
        return 1.0/float(fit)

    def updateChooseProb(self, sumFit):
        self.chooseProb = self.fit / sumFit

    def moveRandSubPathLeft(self):
       # print(n/5)
        path = random.randrange(int(n/5))  # choose a path 
     #   print(path)
        index = self.data.index(CENTER, path+1) # move to the chosen index
      #  print(index)
        # move first CENTER
        locToInsert = 0
        self.data.insert(locToInsert, self.data.pop(index))
        index += 1
        locToInsert += 1
        # move data after CENTER
        while self.data[index] != CENTER:
            self.data.insert(locToInsert, self.data.pop(index))
            index += 1
            locToInsert += 1
        assert(self.length+k >= len(self.data))

    # plot this gene in a new window
    def plot(self):
        Xorder = [X[i] for i in self.data]
        
        Yorder = [Y[i] for i in self.data]
        plt.plot(Xorder, Yorder, c='black', zorder=1)

        plt.scatter(Xorder, Yorder, s = 40, c ='blue',zorder=2)

        plt.scatter(Xorder[0], Yorder[0], s = 60, marker='o', c = 'orange', zorder=3)
        c_x = []
        c_y = []
        for i in Node[-m:]:
            c_x.append(X[i])
            c_y.append(Y[i])
        plt.scatter(c_x, c_y, marker='^',s = 50, c = 'red', zorder=3)

        plt.title(self.name)
        plt.show()


def getSumFit(genes):
    sum = 0
    for gene in genes:
        sum += gene.fit
    return sum


# return a bunch of random genes
def getRandomGenes(size, Node):
    genes = []
    for i in range(len(initial)):
        print(i)
        genes.append(Gene("Gene "+str(i),initial[i]))
        print(genes[i].data,1.0/genes[i].fit)

    #for i in range(4):
     #   print(genes[i].data)
    for i in range(size):
        if i >= len(initial):
            Node_test = deepcopy(Node)
        #print(i)
            genes.append(Gene("Gene "+str(i),Node_test,null = True))
    return genes


# 计算适应度和
def getSumFit(genes):
    sumFit = 0
    for gene in genes:
        sumFit += gene.fit
    return sumFit


# 更新选择概率
def updateChooseProb(genes):
    sumFit = getSumFit(genes)
    for gene in genes:
        gene.updateChooseProb(sumFit)


# 计算累计概率
def getSumProb(genes):
    sum = 0
    for gene in genes:
        sum += gene.chooseProb
    return sum


# 选择复制，选择前 1/3
def choose(genes):
    num = int(geneNum/6) * 2    # 选择偶数个，方便下一步交叉
    # sort genes with respect to chooseProb
    key = lambda gene: gene.chooseProb
    genes.sort(reverse=True, key=key)
    # return shuffled top 1/3
    return genes[0:num]

# 交叉一对
def crossPair(gene1, gene2, crossedGenes):
   # print(22222222222222222,gene1.data)
    gene1.moveRandSubPathLeft()

    gene2.moveRandSubPathLeft()
    v1_num = gene1.data.count(0)
    v2_num = gene2.data.count(0)
    #print(v1_num,v2_num,gene1.data,gene2.data)
    newGene1 = []
    newGene2 = []
    # copy first paths
    centers = 0
    firstPos1 = 1
    for pos in gene1.data:
        firstPos1 += 1
        centers += (pos == CENTER)
        newGene1.append(pos)
        if centers >= v1_num-2:
            break
    #print('first',firstPos1)
    centers = 0
    firstPos2 = 1
    for pos in gene2.data:
        firstPos2 += 1
        centers += (pos == CENTER)
        newGene2.append(pos)
        if centers >= v2_num-2:
            break
    #print('seconde',firstPos2)
    #print('yes',newGene1,newGene2)
    t_1 = len(newGene1)
    t_2 = len(newGene2)
    # copy data not exits in father gene
    for pos in gene2.data:
        if pos not in newGene1:
            newGene1.append(pos)
    for pos in gene1.data:
        if pos not in newGene2:
            newGene2.append(pos)
    # add center at end
    newGene1.append(CENTER)
    newGene2.append(CENTER)
    #print('t1',newGene1)
    #print('t2',newGene2)

    # 计算适应度最高的
    key = lambda gene: gene.fit
    possible = []
    #print('each1',firstPos1,len(gene1.data),gene1.data[firstPos1],gene1.data[firstPos1-1])

    while firstPos1 <= len(gene1.data)-3:
     #   print(firstPos1,777777777777777777777777)
        newGene = copy.copy(newGene1)
        newGene.insert(firstPos1, CENTER)
        newGene = Gene(node=copy.copy(newGene))
        possible.append(newGene)
        firstPos1 += 1
    #print(44444444444444444444444)
    possible.sort(reverse=True, key=key)
    #print(possible[0].data)
    assert(possible)
    crossedGenes.append(possible[0])
    
    key = lambda gene: gene.fit
    possible = []
    #print('each',firstPos2,gene2.data[firstPos2],gene2.data[firstPos2-1])
    while firstPos2 <= len(gene2.data)-3:
       # print(7777777777777777777)
      #  print('each',firstPos2,gene2.data[firstPos2])
        newGene = copy.copy(newGene2)
        newGene.insert(firstPos2, CENTER)
        newGene = Gene(node=copy.copy(newGene))
     #   print('each',gene2.data[firstPos2],newGene.data)
        possible.append(newGene)
        firstPos2 += 1
    #print(555555555555555555555)
    possible.sort(reverse=True, key=key)
    #print(possible[0].data)
    crossedGenes.append(possible[0])
    #print('final')

# 交叉
def cross(genes):
    crossedGenes = []
    for i in range(0, len(genes), 2):
        #print(i)
        #print(i,genes[i].data,genes[i+1].data)
        crossPair(genes[i], genes[i+1], crossedGenes)
    return crossedGenes



# 合并
def mergeGenes(genes, crossedGenes):
    # sort genes with respect to chooseProb
    key = lambda gene: gene.chooseProb
    genes.sort(reverse=True, key=key)
    pos = geneNum - 1
    for gene in crossedGenes:
        genes[pos] = gene
        pos -= 1
    return  genes


# 变异一个
def varyOne(gene):
    varyNum = 30
    variedGenes = []
    for i in range(varyNum):
        #print(i,gene.data)
        p1= random.choice(list(range(1,len(gene.data)-2)))
        p2= random.choice(list(range(1,len(gene.data)-2)))
       #print(p1,p2)
        newGene = copy.copy(gene.data)
        if newGene[p1] != 0 and newGene[p2] != 0 and newGene[p1] != newGene[p2]:
            newGene[p1], newGene[p2] = newGene[p2], newGene[p1] # 交换
        #print('after swap',newGene)
        variedGenes.append(Gene(node=copy.copy(newGene)))
    key = lambda gene: gene.fit
    variedGenes.sort(reverse=True, key=key)
    return variedGenes[0]


# 变异
def vary(genes):
    for index, gene in enumerate(genes):
        #print(index)
        # 精英主义，保留前三十
        if index < 30:
            continue
        if random.random() < VARY:
            genes[index] = varyOne(gene)
    return genes

def charge(gene):
    station = [1001,1025,1026,1028,1042,1044,1050,1051,1068,1069,1071,1094,1095,1098]
    #print(gene.data)
    for i in range(len(gene.data)):
     #   print('gene',i,gene.data[i])
        if gene.data[i] >1000:            
            newgene = copy.copy(gene.data)
            best_fit = copy.copy(gene.fit)
      #      print('station',newgene,1/best_fit)
            for s in station:
       #         print('start',s)
                newgene[i] = s
        #        print(newgene)
                newGene = Gene(node=copy.copy(newgene))
                temp_fit = newGene.fit
         #       print('after change',s,1/temp_fit)
                if temp_fit>best_fit:
                    best_fit = copy.copy(temp_fit)
                    gene = Gene(node = copy.copy(newGene.data))
          #          print('!!!!!!!!!!!!!!!!!!!!!')
        #print('jiuxia',gene.data)
    #print(gene.data)    
    return gene
            
def change(genes):
    for index,gene in enumerate(genes):
        if index <10:
            genes[index] = charge(gene)
    return genes
    
if __name__ == "__main__" and not DEBUG:
    genes = getRandomGenes(geneNum,Node) # 初始种群
    print(len(genes))
    #for i in range(len(genes)):
     #   print(genes[i].name,genes[i].data)
    # 迭代
    for i in range(generationNum):
        print(i)
        updateChooseProb(genes)   
        sumProb = getSumProb(genes)     
        #print(111111111111111)
        chosenGenes = choose(deepcopy(genes))   # 选择
        print(i,'choose yes')
        #for x in range(len(chosenGenes)):
         #   print('chosengenes',x,chosenGenes[x].data)
        crossedGenes = cross(chosenGenes)   # 交叉
        print(i,'crossed yes')
        #for x in range(len(crossedGenes)):
         #   print('crossedgenes',x,crossedGenes[x].data)
        genes = mergeGenes(genes, crossedGenes) # 复制交叉至子代种群
        print(i,'merge yes')
        genes = vary(genes) # under construction
        print(i,'vary yes')
        
    # sort genes with respect to chooseProb
    key = lambda gene: gene.fit
    genes.sort(reverse=True, key=key)   # 以fit对种群排序
    print(1.0/genes[0].fit)
    genes = change(genes)
    genes.sort(reverse=True, key=key)   # 以fit对种群排序
    print('\r\n')
    print('data:', genes[0].data)
    print('fit:', 1.0/genes[0].fit)
    genes[0].plot() # 画出来


if DEBUG:
    print("START")
    gene = Gene()
    print(gene.data)
    gene.moveRandSubPathLeft()
    print(gene.data)


    print("FINISH")

