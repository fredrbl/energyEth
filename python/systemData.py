

import random

## 10 nodes
numNodes = 10

## 1 day => 24 hours, one step is one hour
steps = 24

## 3 nodes have with batteries (could be car, could be something different)
#

## 4 nodes with inflexible supply
numSupply = 4
binary = ['' for i in range(0, numSupply)]
total = 0
for s in range (0, numSupply):
    for t in range(0,steps):
        temp = random.randint(0, 1)
        binary[s] = str(temp)+ binary[s]
        total = total + temp # Total is the total supply we have to cover with demand
    Duration.transact({'from': web3.eth.accounts[s]}).setNode(0, '', binary[s])

## 6 nodes with flexible demand
# The lowest and highest price is arbitralery set to 150 and 600
numDemand = 6
demandString = ['' for i in range(0, numDemand)]
demandHours = [0 for i in range(0, numDemand)]
i = 0
while (total > sum(demandHours)):
    demandHours[i] = demandHours[i] + 1
    i = i + 1
    if (i == numDemand): i = 0
for d in range(0, numDemand):
    for t in range(0, steps):
        demandString[d] = str(random.randint(150, 600)) + ',' + demandString[d]
    Duration.transact({'from': web3.eth.accounts[d + s]}).setNode(demandHours[d], demandString[d], '')
