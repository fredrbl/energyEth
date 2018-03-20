
# Followup after initialiseSystem
import copy
from web3 import Web3, HTTPProvider
import json
import random
import match
import time
import numpy as np
import matplotlib.pyplot as plt
import FlexCoin

# Compile and deploy in populus in one terminal and testrpc-py in another
# Open a new terminal and run this python script in python3
web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/energyEth/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['RealTime']['abi']
address = input("What is the contract address? - RealTime: ")
RealTime = web3.eth.contract(address, abi = abi)
#numHouses = FlexCoin.FlexCoin.call().numHouses()
createNodeCost = []

testRange = range(600, 601, 1)

averageNode = [0 for i in testRange]
averageCentral = [0 for i in testRange]
numTxCentral = [0 for i in testRange]
numTxNodes = [0 for i in testRange]
numTxInitiate = [0 for i in testRange]

def setPrice(battery):
    # One battery have randomised price, the two others have a somewhat smart algorithm
    price = [[0 for x in range(numHouses)] for y in range(2)]
    #price[0][0] = random.randint(480, 590)
    #price[1][0] = random.randint(350, 460)

    for i in range(0, 10, 2): # could show graph over the logic of the pricing
        if (battery[i] <= 6700):
            price[0][i] = random.randint(480, 590) #int(round(480 + battery[i] * 0.0164))
            price[1][i] = random.randint(350, 460) #int(round(460 - battery[i] * 0.0164))
        else:
            price[0][i] = random.randint(480, 590) #int(round(700 - battery[i] * 0.0164))
            price[1][i] = random.randint(350, 460) #int(round(240 + battery[i] * 0.0164))
    return price

def setFlexibility(battery, batteryFlag, numHouses):
    # 5000 w in one hour = 5000 wh => 833 w max in 10 minutes
    availableFlex = [[0 for x in range(numHouses)] for y in range(2)]
    for i in range(0,numHouses):
        if (battery[i] > 840 and battery[i] < 12500):
            availableFlex[0][i] = 700
            availableFlex[1][i] = 700
        elif (battery[i] <= 840 and batteryFlag[i] == 1):
            availableFlex[0][i] = 0
            availableFlex[1][i] = 700
        elif (battery[i] >= 12500):
            availableFlex[0][i] = 700
            availableFlex[1][i] = 0
    return availableFlex

def trade(numTxCentral, numTxNodes, numTxInitiate, price, battery, availableFlex, deviation, numHouses):
    wholesalePrice = 470 # 10cent/kWh
    flexFlag = -1
    transactions = [[] for y in range(3)]
    upPrice = [[0 for x in range(numHouses)] for y in range(2)]
    upPrice[0] = [x for x in range(numHouses)]
    upPrice[1] = price[0]
    downPrice = [[0 for x in range(numHouses)] for y in range(2)]
    downPrice[0] = [x for x in range(numHouses)]
    downPrice[1] = price[1]
    upAvailableFlex = [[0 for x in range(numHouses)] for y in range(2)]
    upAvailableFlex[0] = [x for x in range(numHouses)]
    upAvailableFlex[1] = availableFlex[0] # This is used if the system needs less consumption
    downAvailableFlex = [[0 for x in range(numHouses)] for y in range(2)]
    downAvailableFlex[0] = [x for x in range(numHouses)]
    downAvailableFlex[1] = availableFlex[1] # This is used if system needs more consumption
    demand = [[] for y in range(2)]
    supply = [[] for y in range(2)]
    updateCost = []
    transferCost = ''
    nodeCost = 0
    centralCost = 0

    # Some houses have flexibility, and no deviation. Other houses have deviation, but no flex. Lets do 50/50
    # This procedure is done by each house, so we might change this.
    for i in range(0,numHouses):

        if (i % 2 == 0):
            updateCost.append(RealTime.transact().setRealTimeNodePrice(i, upPrice[1][i], downPrice[1][i]))
            updateCost.append(RealTime.transact().setRealTimeNodeBattery(i, upAvailableFlex[1][i], downAvailableFlex[1][i], 0))
            numTxNodes = numTxNodes + 2
        else:
            updateCost.append(RealTime.transact().setRealTimeNodePrice(i, 0, 0))
            updateCost.append(RealTime.transact().setRealTimeNodeBattery(i, 0, 0, deviation[i]))
            numTxNodes = numTxNodes + 2

    for i in range(0,numHouses):
        h = RealTime.call().getRealTimeNode(i)
        # Up means that the battery must sell energy -> upPrice > wholesalePrice
    #        upPrice[0].append(i)
    #        upPrice[1].append(h[0])
    #        downPrice[0].append(i)
    #        downPrice[1].append(h[1])
    #        upAvailableFlex[0].append(i)
    #        upAvailableFlex[1].append(h[2])
    #        downAvailableFlex[0].append(i)
    #        downAvailableFlex[1].append(h[3])
        if (h[5] < 0):
            demand[0].append(i)
            demand[1].append(-h[5])
        elif (h[5] > 0):
            supply[0].append(i)
            supply[1].append(h[5])

    ################################################################################
    ######## Here the initialisation should end, and other functions take over #####
    ################################################################################

    flexFlag, transactions, restEnergy = match.matching(flexFlag, transactions, demand, supply)

    numTransactionsFirstRound = len(transactions[0])

    if(sum(restEnergy[1]) == 0):  # This means that supply and demand cancel each other, and no more trading is necessary
        flexFlag = 2
        marketPrice = wholesalePrice

    sortedPrice = [[0 for x in range(numHouses)] for y in range(2)]
    copySortedPrice = [[0 for x in range(numHouses)] for y in range(2)]

    # Sort los listas de precio
    # Mark that all prices only must consist of the nodes that is included in the trading

    i = 0
    if (flexFlag == 0):
        demandFlex = copy.deepcopy(upAvailableFlex)
        supplyFlex = restEnergy
        sortedPrice = copy.deepcopy(upPrice)
        copySortedPrice = copy.deepcopy(upPrice)
        sortedPrice[1] = sorted(sortedPrice[1])
        for i in range(len(upPrice[1])):
            sortedPrice[0][i] = copySortedPrice[0][copySortedPrice[1].index(sortedPrice[1][i])]
            demandFlex[1][i] = upAvailableFlex[1][copySortedPrice[1].index(sortedPrice[1][i])]
            demandFlex[0][i] = sortedPrice[0][i]
            copySortedPrice[1][copySortedPrice[1].index(sortedPrice[1][i])] = -1
    else:
        demandFlex = restEnergy
        supplyFlex = copy.deepcopy(downAvailableFlex)
        sortedPrice = copy.deepcopy(downPrice)
        copySortedPrice = copy.deepcopy(downPrice)
        sortedPrice[1] = sorted(sortedPrice[1], reverse = True)
        for i in range(len(downPrice[1])):
            sortedPrice[0][i] = copySortedPrice[0][copySortedPrice[1].index(sortedPrice[1][i])]
            supplyFlex[1][i] = downAvailableFlex[1][copySortedPrice[1].index(sortedPrice[1][i])]
            supplyFlex[0][i] = sortedPrice[0][i]
            copySortedPrice[1][copySortedPrice[1].index(sortedPrice[1][i])] = -1

    firstFlexFlag = copy.deepcopy(flexFlag)
    flexFlag, transactions, restEnergy = match.matching(flexFlag, transactions, demandFlex, supplyFlex)

    if (firstFlexFlag == 0):
        if(flexFlag == 0):
            wholesale = sum(restEnergy[1])
            marketPrice = wholesalePrice
            lastBattery = -1
            print("The system are still ",wholesale," kWh over the bid amount")
        else:
            lastBattery = transactions[1][len(transactions[0]) - 1]
            marketPrice = sortedPrice[1][sortedPrice[0].index(lastBattery)]
            print('The systems batteries can cover the deviations')
    elif(firstFlexFlag == 1):
        if(flexFlag == 0):
            lastBattery = transactions[0][len(transactions[0]) - 1]
            marketPrice = sortedPrice[1][sortedPrice[0].index(lastBattery)]
            print('The systems batteries can cover the deviations')
        else:
            wholesale = sum(restEnergy[1])
            marketPrice = wholesalePrice
            lastBattery = -1
            print("The system are still ",wholesale," kWh under the bid amount")

    ################################################################################
    ### The calculation is done, and the transactions are performed in blockchain ##
    ################################################################################
    numTxCentral = len(transactions[0])
    print(len(transactions[0]), len(transactions[1]), len(transactions[2]))
    transferCost = RealTime.transact().checkAndTransactList(firstFlexFlag, sortedPrice[0], sortedPrice[1], transactions[0], transactions[1], transactions[2], marketPrice, FlexCoin.address)
    centralCost = web3.eth.getTransactionReceipt(transferCost).gasUsed

    if (firstFlexFlag == 0):
        for i in range(numTransactionsFirstRound,len(transactions[0])):
            battery[transactions[1][i]] = battery[transactions[1][i]] - transactions[2][i]
    if (firstFlexFlag == 1):
        for i in range(numTransactionsFirstRound,len(transactions[0])):
            battery[transactions[0][i]] = battery[transactions[0][i]] + transactions[2][i]
    for i in range(0, len(updateCost)):
        nodeCost = web3.eth.getTransactionReceipt(updateCost[i]).gasUsed + nodeCost
    #for i in range(0, len(createNodeCost)):
    #    nodeCost = web3.eth.getTransactionReceipt(createNodeCost[i]).gasUsed + nodeCost

    return(numTxCentral, numTxNodes, numTxInitiate, battery, marketPrice, nodeCost, centralCost)

######## Now, we could test the system over a certain set of time steps
def testRealTime(numHouses, numPeriods):
    i = 0

    #####################################################################################
    ####### The loop below is called if there not are premade sufficient houses in FlexCoin
    ####### If creates new nodes in the blockchain network, and giving them ether, which is necessary in order to trade
    ####### Thereafter, it is created a new house from its address
    #####################################################################################
    while (FlexCoin.FlexCoin.call().numHouses() < numHouses):
        web3.personal.newAccount('pass') # Pass is the password necessary to unlock the account.
        web3.personal.unlockAccount(web3.eth.accounts[FlexCoin.FlexCoin.call().numHouses()], 'pass')
        web3.eth.sendTransaction({'to': web3.eth.accounts[FlexCoin.FlexCoin.call().numHouses()], 'from': web3.eth.coinbase, 'value': 123456789})
        ################# Now, the new node is created, and have an amount of ether. We must now create a house in his address
        FlexCoin.FlexCoin.transact().newHouse({'from': web3.eth.accounts[FlexCoin.FlexCoin.call().numHouses()]})

    ### The variables below is used to measure the amount of transactions which is done in the system
    ## Central is the central node, node is how many each node sends in, and initiate is when a new account is initiated.
    numTxCentral = 0
    numTxNodes = 0
    numTxInitiate = 0

    for i in range(0,numHouses):
        createNodeCost.append(RealTime.transact().newRealTimeNode(web3.eth.accounts[i]))
        numTxInitiate = numTxInitiate + 1

    deviation = [[0 for x in range(numHouses)] for y in range(numPeriods)]
    battery = [[0 for x in range(numHouses)] for y in range(numPeriods)]
    batteryFlag = [0 for x in range(0,numHouses)]
    price = [[[0 for z in range(numHouses)] for x in range(0, 2)] for y in range(numPeriods)]
    nodeCost = [0 for i in range(numPeriods)]
    centralCost = [0 for i in range(numPeriods)]
    flexCoinBalance = [[0 for x in range(numHouses)] for y in range(numPeriods)]

    for i in range(0, numHouses):
        if (i % 2 == 0):
            battery[0][i] = 6700
            batteryFlag[i] = 1

    ## Randomising deviations and price
    for i in range(0, numPeriods):
        for j in range(0, numHouses):
            deviation[i][j] = random.randint(-500, 500)
            price[i][0][j] = random.randint(480, 590)
            price[i][1][j] = random.randint(350, 460)

    for j in range(0,numHouses):
        _, flexCoinBalance[0][j] = FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[j])
    marketPrice = [RealTime.call().wholesalePrice() for x in range(0,numPeriods)]

    for i in range(0, numPeriods): #144 for a whole day

        ### Setting the deviations.
        for j in range(0,numHouses):
            if ((battery[i - 1][j] > deviation[i][j]) and (battery[i - 1][j] < deviation[i][j] + 13500) and (batteryFlag[j] == 1)):
                battery[i][j] = battery[i - 1][j] + deviation[i][j]  # If deviation not is included, the batteries work without
                # deviation[i][j] = 0 # It is being set to zero later anyway
            else:
                if (deviation[i][j] < 0 and batteryFlag == 1):
                    deviation[i][j] = deviation[i][j] + (13500 - battery[i][j])
                    battery[i][j] = 13500
                else:
                    deviation[i][j] = deviation[i][j] - battery[i][j]
                    battery[i][j] = 0

        ### Now, we must set the price based on the battery status. This thesis have chosen not to use this function, and rather use a randomised price for each time.
        ## If a user wants to set a different price (which should be done), it is recommended to use setPrice function.
        # price[i] = setPrice(battery[i])

        ### Set the available flexibility in each battery
        availableFlex = setFlexibility(battery[i], batteryFlag, numHouses)

        ### The trading happens, and the batteries are corrected for the trading
        numTxCentral, numTxNodes, numTxInitiate, battery[i], marketPrice[i], nodeCost[i], centralCost[i] = trade(numTxCentral, numTxNodes, numTxInitiate, price[i], battery[i], availableFlex, deviation[i], numHouses)
        for j in range(0,numHouses):
            if (battery[i][j] > battery[i - 1][j]):
                battery[i][j] = round(int(0.9 * battery[i][j]))
            _, flexCoinBalance[i][j] = FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[j])

    averageNode = (sum(nodeCost)/numPeriods)
    averageCentral = sum(centralCost)/numPeriods
    return numTxCentral, numTxNodes, numTxInitiate, flexCoinBalance, battery, price, deviation, marketPrice, averageNode, averageCentral


#### The simulation is now performed. The main results is averageCentral and averageNode, where these provides with the gas results from the central calculation and the nodes
counter = 0
node = [0 for i in testRange]
total = [0 for i in testRange]
for i in testRange:
    numTxCentral[counter], numTxNodes[counter], numTxInitiate[counter], flexCoinBalance, battery, price, deviation, marketPrice, averageNode[counter], averageCentral[counter] = testRealTime(i, 1)
    total[counter] = node[counter] + averageCentral[counter]
    counter = counter + 1
