from web3 import Web3, HTTPProvider
import json
import FlexCoin
import numpy as np
import random
import copy
import matplotlib.pyplot as plt

############### ASSUMPTIONS ###############
# This is a simplified python script. The following assumptions hold;
# - The loads must be available at all times (i.e a price between 1 -> 998)
# - The energy for one hour is always 1 kwh, both for supply and demand
# - The energy is always divided in one hour.
# - That supp and demand is the same size => perfectly adequate.

web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/energyEth/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['Duration']['abi']
address = input("What is the contract address? - Duration: ")
Duration = web3.eth.contract(address, abi = abi)

def nodeSensitivity(start, stop, steps):
# This function performs sensitivity on the amount of nodes in the day ahead trading

    # results is both marginal prices and total cost
    nodes = range(start, stop, 1)
    demandCost = [0 for n in range(0, stop)]
    supplyCost = [0 for n in range(0, stop)]
    centralCost = [0 for n in range(0, stop)]
    iterator = 0
    margCost = [0 for t in range(0, 144)]

    # This for loop initialises and prepares the houses for trading
    for i in range(0, stop):
        flag = 0
        if(len(web3.eth.accounts) <= i):
            web3.personal.newAccount('pass')
            web3.personal.unlockAccount(web3.eth.accounts[i], 'pass')
            flag = 1

        # If the nodes does not have enough ether to perform transactions, this is runned
        if(web3.eth.getBalance(web3.eth.accounts[i]) < 99999999999):
            web3.eth.sendTransaction({'to': web3.eth.accounts[i], 'from': web3.eth.coinbase, 'value': 9999999999999999})

        # Here the new nodes get a house
        if(flag == 1):
            FlexCoin.FlexCoin.transact({'from': web3.eth.accounts[i]}).newHouse()

    # This increases the node amount, and performs the trading. The if loop inside is for dividing the supply and demand side in even and odd numbers.
    for n in nodes:
        if(n % 2 == 0):
            demandCost[n], supplyCost[n] = setSystemData(int(n/2), int(n/2), steps)
            owner, demandHours, supplyHours, demandPrices = getSystemData(n, steps, iterator)
            centralCost[n] = matching(owner, demandHours, supplyHours, demandPrices, steps)
            iterator = iterator + 1

        else:
            demandCost[n], supplyCost[n] = setSystemData(int((n + 1)/2), int((n - 1)/2), steps)
            owner, demandHours, supplyHours, demandPrices = getSystemData(n, steps, iterator)
            centralCost[n] = matching(owner, demandHours, supplyHours, demandPrices, steps)
            iterator = iterator + 1

    return centralCost, demandCost, supplyCost


def stepSensitivity(numNodes, start, stop):
# This function performs sensitivity on the amount of time steps in the day ahead trading

    # results is both marginal prices and total cost
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
        demandCost[t], supplyCost[t] = setSystemData(_numSupply, _numDemand, t)
        owner, demandHours, supplyHours, demandPrices = getSystemData(numNodes, t, iterator)
        centralCost[t] = matching(owner, demandHours, supplyHours, demandPrices, t)
        iterator = iterator + 1

    return centralCost, demandCost, supplyCost

#### FUNCTIONS ####
def setSystemData(_numSupply, _numDemand, _steps):
#This function sets in energy data for the supply and demand side into the blockchain

    binary = ['' for i in range(0, _numSupply)]
    total = 0
    supplyCost = 0
    demandCost = 0

    # This for loop fills in randomised energy data for the supply side, s
    for s in range (0, _numSupply):
        for t in range(0,_steps):
            tempBin = random.randint(0, 1)
            binary[s] = str(tempBin)+ binary[s]
            total = total + tempBin # Total is the total supply we have to cover with demand
        if(web3.eth.getBalance(web3.eth.accounts[s]) < 99999999999):
            web3.personal.unlockAccount(web3.eth.accounts[s], 'pass')
            web3.eth.sendTransaction({'to': web3.eth.accounts[s], 'from': web3.eth.coinbase, 'value': 999999999999})
        tempCost = Duration.transact({'from': web3.eth.accounts[s]}).setNode(0, '', binary[s])
        supplyCost = web3.eth.getTransactionReceipt(tempCost).gasUsed + supplyCost

    demandString = ['' for i in range(0, _numDemand)]
    demandHours = [0 for i in range(0, _numDemand)]
    i = 0

    # This while and for loop fills in randomised energy data for the demand side, d
    while (total > sum(demandHours)):
        demandHours[i] = demandHours[i] + 1
        i = i + 1
        if (i == _numDemand): i = 0
    for d in range(0, _numDemand):
        for t in range(0, _steps):
            # The lowest and highest price is arbitralery set to 150 and 600
            demandString[d] = str(random.randint(150, 600)) + ',' + demandString[d]
        if(web3.eth.getBalance(web3.eth.accounts[(d + 1) + s]) < 99999999999):
            web3.personal.unlockAccount(web3.eth.accounts[(d + 1) + s], 'pass')
            web3.eth.sendTransaction({'to': web3.eth.accounts[(d + 1) + s], 'from': web3.eth.coinbase, 'value': 999999999999})
        tempCost = Duration.transact({'from': web3.eth.accounts[(d + 1) + s]}).setNode(demandHours[d], demandString[d], '')
        demandCost = web3.eth.getTransactionReceipt(tempCost).gasUsed + demandCost
    return demandCost, supplyCost

def getSystemData(_numNodes, _steps, iterator):
# This function fetches the energy data from the blockchain

    owner = ["0" for i in range(0, _numNodes)]
    demandHours = [0 for i in range(0, _numNodes)]
    tempDemandPrices = [['' for x in range(0, _steps)] for y in range(0, _numNodes)]
    endDemandPrices = [[999 for x in range(0, _steps)] for y in range(0, _numNodes)]
    endSupplyHours = [[0 for x in range(0, _steps)] for y in range(0, _numNodes)]
    for n in range(0, _numNodes):
        lastNodeID = Duration.call().numNodes() - 1
        firstNodeID = lastNodeID - _numNodes + 1
        owner[n], demandHours[n], demandPrices, supplyHours = Duration.call().getNode(firstNodeID + n)
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

def matching(owner, demandHours, supplyHours, demandPrices, steps):
# This function is the market calculation, in addition to performing the payment

    sortedList = [[] for t in range(0, steps)]
    addressFrom = [[] for t in range(0, steps)]
    addressTo = [[] for t in range(0, steps)]
    copyDemandPrices = copy.deepcopy(demandPrices.tolist())
    cost = 0
    tempCost = ''
    for t in range(0,steps):

        # The following for loop matches supply and demand and puts the transactions in vectors
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

        # The following if and for loop performs payment, using the FlexCoin contract.
        if(len(sortedList[t]) > 0):
            for a in range(0, (len(web3.eth.accounts) - 1)):
                add, bal = FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[a])
                if bal == 0:
                    FlexCoin.FlexCoin.transact({'from': web3.eth.accounts[a]}).newHouse()
            tempCost = Duration.transact().checkAndTransfer(sortedList[t], addressFrom[t], addressTo[t], copyDemandPrices[t], t, FlexCoin.address)
            cost = web3.eth.getTransactionReceipt(tempCost).gasUsed + cost
    return cost
