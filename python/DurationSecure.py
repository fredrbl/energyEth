from web3 import Web3, HTTPProvider
import json
import FlexCoin
import numpy as np
import random
import copy
import matplotlib.pyplot as plt

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

abi = values['DurationSecure']['abi']
address = input("What is the contract address? - DurationSecure: ")
DurationSecure = web3.eth.contract(address, abi = abi)

totTransactions = 0
### MAIN ###

def nodeSensitivity(start, stop, steps):
    # results is both marginal prices and total cost
    nodes = range(start, stop, 1)
    demandCost = [0 for n in range(0, stop)]
    supplyCost = [0 for n in range(0, stop)]
    centralCost = [0 for n in range(0, stop)]
    iterator = 0
    margCost = [0 for t in range(0, 144)]

    for i in range(0, stop):
        flag = 0
        if(len(web3.eth.accounts) <= i):
            web3.personal.newAccount('pass')
            web3.personal.unlockAccount(web3.eth.accounts[i], 'pass')
            if(web3.eth.getBalance(web3.eth.accounts[i]) < 123456789101112131415):
                web3.eth.sendTransaction({'to': web3.eth.accounts[i], 'from': web3.eth.coinbase, 'value': 123456789101112131415})
            FlexCoin.FlexCoin.transact({'from': web3.eth.accounts[i]}).newHouse()
        if(web3.eth.getBalance(web3.eth.accounts[i]) < 123456789101112131415):
            web3.eth.sendTransaction({'to': web3.eth.accounts[i], 'from': web3.eth.coinbase, 'value': 123456789101112131415})
        add, tot = FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[i])
    input('pause')
    for n in nodes:
        if(n % 2 == 0):
            demandCost[n], supplyCost[n] = setSystemData(int(n/2), int(n/2), steps)
            owner, demandHours, supplyHours, demandPrices = getSystemData(n, steps, iterator)
            centralCost[n] = matching(owner, demandHours, supplyHours, demandPrices, steps)
            iterator = iterator + 1
            if (n > 2):
                margCost[n] = centralCost[n] - centralCost[n - 1]
        else:
            demandCost[n], supplyCost[n] = setSystemData(int((n + 1)/2), int((n - 1)/2), steps)
            owner, demandHours, supplyHours, demandPrices = getSystemData(n, steps, iterator)
            centralCost[n] = matching(owner, demandHours, supplyHours, demandPrices, steps)
            iterator = iterator + 1
            if (n > 2):
                margCost[n] = centralCost[n] - centralCost[n - 1]
        print("node done")

    #### Plot la diferencia, y mostrar la marginal crecimiento.
    centralCost = np.asarray(centralCost)
    margCost = np.asarray(margCost)
    x = np.arange(start, stop, 1)
    yCost = centralCost[x]
    yMargCost = margCost[x]

    costPlt  = plt.figure(1)
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.plot(x, yCost, '-o')
    costPlt.show()

    margPlt = plt.figure(2)
    plt.xticks(np.arange(x.min(), x.max(), 1))
    plt.plot(x, yMargCost, '-o')
    margPlt.show()

    return centralCost, demandCost, supplyCost

def stepSensitivity(numNodes, start, stop):
    # results is both marginal prices and total cost
    # This is done with 10 nodes as standard
    steps = range(start, stop, 24)
    demandCost = [0 for t in range(0, stop)]
    supplyCost = [0 for t in range(0, stop)]
    centralCost = [0 for t in range(0, stop)]
    if(numNodes % 2 == 0):
        _numDemand = int(numNodes / 2)
    else:
        _numDemand = int((numNodes + 1) / 2)
    _numSupply = numNodes - _numDemand

    iterator = 0
    margCost = [0 for t in range(0, stop)]
    for t in steps:
    ## to open many accounts-> dont know. wait for response during your trip. Mientras ese, construir tu codigo
        demandCost[t], supplyCost[t] = setSystemData(_numSupply, _numDemand, t)
        owner, demandHours, supplyHours, demandPrices = getSystemData(numNodes, t, iterator)
        centralCost[t] = matching(owner, demandHours, supplyHours, demandPrices, t)
        iterator = iterator + 1
        if (t > 24):
            margCost[t] = centralCost[t] - centralCost[t - 24]
        print("time step done")
    #### Plot la diferencia, y mostrar la marginal crecimiento.
    centralCost = np.asarray(centralCost)
    margCost = np.asarray(margCost)
    x = np.arange(start, stop, 24)
    yCost = centralCost[x]
    yMargCost = margCost[x]

    costPlt  = plt.figure(24)
    plt.xticks(np.arange(x.min(), x.max(), 24))
    plt.plot(x, yCost, '-o')
    costPlt.show()

    margPlt = plt.figure(2)
    plt.xticks(np.arange(x.min(), x.max(), 24))
    plt.plot(x, yMargCost, '-o')
    margPlt.show()

    return centralCost, demandCost, supplyCost
    ## quiza mostrarlo en dos plots..
#### FUNCTIONS ####

def setSystemData(_numSupply, _numDemand, _steps):
    ## 4 nodes with inflexible supply
    global totTransactions
    binary = [[0 for x in range(0, _steps)] for y in range(0, _numSupply)]
    total = 0
    supplyCost = 0
    demandCost = 0
    for s in range (0, _numSupply):
        for t in range(0,_steps):
            binary[s][t] = random.randint(0, 1)
            total = total + binary[s][t] # Total is the total supply we have to cover with demand
        if(web3.eth.getBalance(web3.eth.accounts[s]) < 123456789101112131415):
            web3.eth.sendTransaction({'to': web3.eth.accounts[s], 'from': web3.eth.coinbase, 'value': 123456789101112131415})
        tempCost = DurationSecure.transact({'from': web3.eth.accounts[s]}).setNode(0, [0], binary[s])
        totTransactions = totTransactions + 1
        supplyCost = web3.eth.getTransactionReceipt(tempCost).gasUsed + supplyCost
    ## 6 nodes with flexible demand
    # The lowest and highest price is arbitralery set to 150 and 600
    demandPrices = [[0 for x in range(0, _steps)] for y in range(0, _numDemand)]
    demandHours = [0 for i in range(0, _numDemand)]
    i = 0
    while (total > sum(demandHours)):
        demandHours[i] = demandHours[i] + 1
        i = i + 1
        if (i == _numDemand): i = 0

    for d in range(0, _numDemand):
        for t in range(0, _steps):
            demandPrices[d][t] = random.randint(150, 600)
        web3.personal.unlockAccount(web3.eth.accounts[(d + 1) + s], 'pass')
        if(web3.eth.getBalance(web3.eth.accounts[d + 1 + s]) < 123456789101112131415):
            web3.eth.sendTransaction({'to': web3.eth.accounts[d+1+s], 'from': web3.eth.coinbase, 'value': 123456789101112131415})
        print(d + 1 + s)
        print(demandHours[d])
        print(demandPrices[d])
        tempCost = DurationSecure.transact({'from': web3.eth.accounts[(d + 1) + s]}).setNode(demandHours[d], demandPrices[d], [0])
        totTransactions = totTransactions + 1
        demandCost = web3.eth.getTransactionReceipt(tempCost).gasUsed + demandCost
    return demandCost, supplyCost

def getSystemData(_numNodes, _steps, iterator):
    owner = ["0" for i in range(0, _numNodes)]
    demandHours = [0 for i in range(0, _numNodes)]
    demandPrices = [[] for y in range(0, _numNodes)]
    supplyHours = [[] for y in range(0, _numNodes)]
    testDemandPrices = [0 for y in range(0, _numNodes)]
    testSupplyHours = [0 for y in range(0, _numNodes)]
    counterDemand = 0
    counterSupply = 0
    for n in range(0, _numNodes):
        lastNodeID = DurationSecure.call().numNodes() - 1
        firstNodeID = lastNodeID - _numNodes + 1
        owner[n], demandHours[n], testDemandPrices[n], testSupplyHours[n] = DurationSecure.call().getNode(firstNodeID + n, 0, 1)
        if(demandHours[n] != 0):
            for t in range(0, _steps):
                supplyHours[n].append(0)
                demandPrices[n].append(DurationSecure.call().getNode(firstNodeID + n, t, 1)[2])
        else:
            for t in range(0, _steps):
                demandPrices[n].append(999)
                supplyHours[n].append(DurationSecure.call().getNode(firstNodeID + n, t, 0)[3])

    demandPrices = (np.array(demandPrices)).transpose()
    supplyHours = (np.array(supplyHours)).transpose()
    return (owner, demandHours, supplyHours, demandPrices)

def matching(owner, demandHours, supplyHours, demandPrices, steps):
    global totTransactions
    sortedList = [[] for t in range(0, steps)]
    addressFrom = [[] for t in range(0, steps)]
    addressTo = [[] for t in range(0, steps)]
    copyDemandPrices = copy.deepcopy(demandPrices.tolist())
    cost = 0
    tempCost = ''
    numNodes = len(supplyHours[0])
    lastNodeID = DurationSecure.call().numNodes() - 1
    firstNodeID = lastNodeID - numNodes + 1
    for t in range(0,steps):
        ## bueno. sort, y create a list of index equal to the list.
        length = np.sum(supplyHours[t])
        for i in range(0, length):
            sortedList[t].append(demandPrices[t].tolist().index(min(demandPrices[t])))
            demandPrices[t][sortedList[t][i]] = 998 # because a node not can give more in one step
            addressFrom[t].append(sortedList[t][i])
            addressTo[t].append(supplyHours[t].tolist().index(1))
            supplyHours[t][supplyHours[t].tolist().index(1)] = 0
            demandHours[sortedList[t][i]] = demandHours[sortedList[t][i]] - 1
            if (demandHours[sortedList[t][i]] == 0): # The demand node is empty, and must be set to 999
                for t2 in range(i, steps):
                    demandPrices[t2][sortedList[t][i]] = 998

        if(length > 0):
            for j in range(0, length):
                addressTo[t][j] = firstNodeID + addressTo[t][j]
                addressFrom[t][j] = firstNodeID + addressFrom[t][j]
                sortedList[t][j] = firstNodeID + sortedList[t][j]
                address1, _, dmp1, _ = DurationSecure.call().getNode(addressTo[t][j], t, 0)
                address2, _, dmp2, _ = DurationSecure.call().getNode(addressFrom[t][j], t, 1)
                FlexCoin.FlexCoin.transact({'from': address1}).newHouse()
                FlexCoin.FlexCoin.transact({'from': address2}).newHouse()
            tempCost = DurationSecure.transact().checkAndTransfer(sortedList[t], addressFrom[t], addressTo[t], t, FlexCoin.address)
            totTransactions = totTransactions + 1
            cost = web3.eth.getTransactionReceipt(tempCost).gasUsed + cost
    return cost

centralCost, demandCost, supplyCost = nodeSensitivity(99, 101, 24)
