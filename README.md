# GOC-EVRPTW
这是京东GOC城市物流运输车辆智能调度比赛前50名的一个解决方案。  
赛题链接：[京东GOC城市物流运输车辆智能调度](https://jdata.jd.com/html/detail.html?id=5)

### 赛题简析  
该题目的VRP考虑了电车的多循环和充电问题。  
题目要求综合成本最少，综合成本是运输成本，等待成本, 充电成本和固定成本的总和，即为目标函数。 
对于约束条件，这里有VRP中常见的最大容量约束(CVRP)、时间窗口约束(VRPTW)、混合车辆约束(Heterogeneous Fleet VRP)、多循环约束(Multi-trip VRP)、带充电站的电车里程约束(Electric VRP with Recharging Stations)。

### 解决思路  
本代码提供了两个思路：  
1.利用聚类分区，从而转化为求解每一个小区域的MIP问题，VRP_SubRegion即是这种方法的实现,使用 run.sh 执行；  
2.分区之后利用遗传算法求解每一个较大区域的遗传问题，并且将方法一中的较优解作为遗传算法的初始种群。

### Requirements  
* python3.6  
* gurobi7.0
* pandas0.23.1  
