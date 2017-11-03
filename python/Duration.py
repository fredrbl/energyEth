from web3 import Web3, HTTPProvider
import json
import FlexCoin
import numpy as np
import random
import copy

############### ASSUMPTIONS ###############
# This is a very simplified method. The following assumptions hold;
# - The loads must be available at all times (i.e a price between 1 -> 998)
# - The energy for one hour is always 1 kwh, both for supply and demand
# - The energy is always divided in one hour.
# - Each node is either a demand or supply node. A node cannot be both
# - That supp and demand is the same size => perfectly adequate.

web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/energyEth/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['Duration']['abi']
address = input("What is the contract address? - Duration: ")
Duration = web3.eth.contract(address, abi = abi)

steps = 24
numNodes = 10
numSupply = 4
numDemand = 6

owner = ["0" for i in range(0, numNodes)]
demandHours = [0 for i in range(0, numNodes)]
demandPrices = [[999 for x in range(0, steps)] for y in range(0, numNodes)]
supplyHours = [[0 for x in range(0, steps)] for y in range(0, numNodes)]
# getter for the demand y supplyHours...!

def setSystemData(_numSupply, _numDemand, _steps):
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

def getSystemData(_numNodes, _steps):
    owner = ["0" for i in range(0, _numNodes)]
    demandHours = [0 for i in range(0, _numNodes)]
    tempDemandPrices = [['' for x in range(0, _steps)] for y in range(0, _numNodes)]
    endDemandPrices = [[999 for x in range(0, _steps)] for y in range(0, _numNodes)]
    endSupplyHours = [[0 for x in range(0, _steps)] for y in range(0, _numNodes)]
    for n in range(0, _numNodes):
        owner[n], demandHours[n], demandPrices, supplyHours = Duration.call().getNode(n)
        i = 0 # i here is the iteratior that converts the strings to integers

        for t in range(0, _steps):
            if(supplyHours == ''):
                while (demandPrices[i] != ','):
                    tempDemandPrices[n][t] =  tempDemandPrices[n][t] + demandPrices[i]
                    i = i + 1
                i = i + 1
                endDemandPrices[n][t] = int(tempDemandPrices[n][t])
            else:
                endSupplyHours[n][t] = int(supplyHours[t])
    endDemandPrices = (np.array(endDemandPrices)).transpose()
    endSupplyHours = (np.array(endSupplyHours)).transpose()

    return (owner, demandHours, endSupplyHours, endDemandPrices)

def matching(supplyHours, demandPrices):
    sortedList = [[] for t in range(0, steps)]
    addressFrom = [[] for t in range(0, steps)]
    addressTo = [[] for t in range(0, steps)]
    copyDemandPrices = copy.deepcopy(demandPrices.tolist())
    for t in range(0,steps):
        ## bueno. sort, y create a list of index equal to the list.
        for i in range(0, np.sum(supplyHours[t])):
            sortedList[t].append(demandPrices[t].tolist().index(min(demandPrices[t])))
            demandPrices[t][sortedList[t][i]] = 999 # because a node not can give more in one step
            addressFrom[t].append(sortedList[t][i])
            addressTo[t].append(supplyHours[t].tolist().index(1))
            supplyHours[t][supplyHours[t].tolist().index(1)] = 0
            demandHours[sortedList[t][i]] = demandHours[sortedList[t][i]] - 1
            if (demandHours[sortedList[t][i]] == 0): # The demand node is empty, and must be set to 999
                for t2 in range(i, steps):
                    demandPrices[t2][sortedList[t][i]] = 999
        print(addressFrom[t])
        print(addressTo[t])
        print(sortedList[t])
        print(copyDemandPrices[t])
        if(len(sortedList[t]) > 0):
            Duration.transact().checkAndTransfer(sortedList[t], addressFrom[t], addressTo[t], copyDemandPrices[t], t, FlexCoin.address)
        print(FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[1]))
        print(FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[2]))
    return sortedList
