
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
_numHouses = FlexCoin.FlexCoin.call().numHouses()

def setPrice(battery):
    # One battery have randomised price, the two others have a somewhat smart algorithm
    price = [[0 for x in range(_numHouses)] for y in range(2)]
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

def setFlexibility(battery, batteryFlag):
    # 5000 w in one hour = 5000 wh => 833 w max in 10 minutes
    availableFlex = [[0 for x in range(_numHouses)] for y in range(2)]
    for i in range(0,_numHouses):
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

def trade(price, battery, availableFlex, deviation):
    wholesalePrice = 470 # 10cent/kWh
    flexFlag = -1
    transactions = [[] for y in range(3)]
    upPrice = [[0 for x in range(_numHouses)] for y in range(2)]
    upPrice[0] = [x for x in range(_numHouses)]
    upPrice[1] = price[0]
    downPrice = [[0 for x in range(_numHouses)] for y in range(2)]
    downPrice[0] = [x for x in range(_numHouses)]
    downPrice[1] = price[1]
    upAvailableFlex = [[0 for x in range(_numHouses)] for y in range(2)]
    upAvailableFlex[0] = [x for x in range(_numHouses)]
    upAvailableFlex[1] = availableFlex[0] # This is used if the system needs less consumption
    downAvailableFlex = [[0 for x in range(_numHouses)] for y in range(2)]
    downAvailableFlex[0] = [x for x in range(_numHouses)]
    downAvailableFlex[1] = availableFlex[1] # This is used if system needs more consumption
    demand = [[] for y in range(2)]
    supply = [[] for y in range(2)]
    createNodeCost = []
    updateCost = []
    transferCost = []
    nodeCost = 0
    centralCost = 0

    # Some houses have flexibility, and no deviation. Other houses have deviation, but no flex. Lets do 50/50
    # This procedure is done by each house, so we might change this.
    for i in range(0,_numHouses):
        createNodeCost.append(RealTime.transact().newRealTimeNode(web3.eth.accounts[i]))
        if (i % 2 == 0):
            updateCost.append(RealTime.transact().setRealTimeNodePrice(i, upPrice[1][i], downPrice[1][i]))
            updateCost.append(RealTime.transact().setRealTimeNodeBattery(i, upAvailableFlex[1][i], downAvailableFlex[1][i], 0))
        else:
            updateCost.append(RealTime.transact().setRealTimeNodePrice(i, 0, 0))
            updateCost.append(RealTime.transact().setRealTimeNodeBattery(i, 0, 0, deviation[i]))

    for i in range(0,_numHouses):
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

    sortedPrice = [[0 for x in range(_numHouses)] for y in range(2)]
    copySortedPrice = [[0 for x in range(_numHouses)] for y in range(2)]

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

    transferCost.append(RealTime.transact().checkAndTransactList(firstFlexFlag, sortedPrice[0], sortedPrice[1], transactions[0], transactions[1], transactions[2], marketPrice, FlexCoin.address))
    if (firstFlexFlag == 0):
        for i in range(numTransactionsFirstRound,len(transactions[0])):
            battery[transactions[1][i]] = battery[transactions[1][i]] - transactions[2][i]
    if (firstFlexFlag == 1):
        for i in range(numTransactionsFirstRound,len(transactions[0])):
            battery[transactions[0][i]] = battery[transactions[0][i]] + transactions[2][i]
    for i in range(0, len(updateCost)):
        nodeCost = web3.eth.getTransactionReceipt(updateCost[i]).gasUsed + nodeCost
    for i in range(0, len(createNodeCost)):
        nodeCost = web3.eth.getTransactionReceipt(createNodeCost[i]).gasUsed + nodeCost
    for i in range(0, len(centralCost)):
        centralCost = web3.eth.getTransactionReceipt(transferCost[i]).gasUsed + centralCost

    return(battery, marketPrice, nodeCost, centralCost)

######## Now, we could test the system over a certain set of time steps
def testRealTime():

    numPeriods = 20
    deviation = [[0 for x in range(_numHouses)] for y in range(numPeriods)]
    battery = [[0 for x in range(_numHouses)] for y in range(numPeriods)]
    cost = [0 for i in range(numPeriods)]
    battery[0] = [6700, 0, 6700, 0, 6700, 0, 6700, 0, 6700, 0] #starting at 50 SOC.s given we have 6 batteries
    batteryFlag = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0] # this batteryFlag tells what kind of battery that are used
    BattEff = 0.9 # Taken from Tesla Powerwall 2.0
    price = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [[492, 0, 509, 0, 541, 0, 577, 0, 537, 0], [441, 0, 386, 0, 419, 0, 444, 0, 378, 0]], [[558, 0, 520, 0, 588, 0, 504, 0, 518, 0], [456, 0, 395, 0, 388, 0, 436, 0, 350, 0]], [[491, 0, 499, 0, 570, 0, 503, 0, 568, 0], [440, 0, 405, 0, 370, 0, 383, 0, 407, 0]], [[537, 0, 589, 0, 584, 0, 551, 0, 536, 0], [388, 0, 423, 0, 356, 0, 358, 0, 430, 0]], [[483, 0, 540, 0, 564, 0, 560, 0, 518, 0], [394, 0, 396, 0, 373, 0, 363, 0, 385, 0]], [[497, 0, 531, 0, 536, 0, 588, 0, 529, 0], [407, 0, 452, 0, 381, 0, 444, 0, 422, 0]], [[566, 0, 499, 0, 512, 0, 501, 0, 551, 0], [380, 0, 367, 0, 393, 0, 424, 0, 398, 0]], [[556, 0, 538, 0, 543, 0, 483, 0, 524, 0], [381, 0, 370, 0, 398, 0, 460, 0, 419, 0]], [[581, 0, 484, 0, 559, 0, 481, 0, 516, 0], [427, 0, 381, 0, 436, 0, 455, 0, 389, 0]], [[584, 0, 503, 0, 504, 0, 530, 0, 583, 0], [382, 0, 377, 0, 409, 0, 415, 0, 408, 0]], [[484, 0, 583, 0, 534, 0, 513, 0, 557, 0], [418, 0, 393, 0, 416, 0, 389, 0, 356, 0]], [[590, 0, 538, 0, 536, 0, 568, 0, 540, 0], [402, 0, 428, 0, 379, 0, 459, 0, 385, 0]], [[483, 0, 489, 0, 532, 0, 482, 0, 575, 0], [447, 0, 407, 0, 455, 0, 380, 0, 427, 0]], [[511, 0, 567, 0, 537, 0, 564, 0, 561, 0], [379, 0, 358, 0, 375, 0, 419, 0, 422, 0]], [[500, 0, 516, 0, 521, 0, 499, 0, 517, 0], [352, 0, 426, 0, 414, 0, 420, 0, 430, 0]], [[528, 0, 500, 0, 516, 0, 544, 0, 489, 0], [356, 0, 362, 0, 460, 0, 441, 0, 400, 0]], [[485, 0, 561, 0, 532, 0, 511, 0, 552, 0], [450, 0, 450, 0, 435, 0, 395, 0, 381, 0]], [[481, 0, 543, 0, 547, 0, 500, 0, 545, 0], [403, 0, 399, 0, 427, 0, 352, 0, 388, 0]], [[518, 0, 588, 0, 588, 0, 480, 0, 563, 0], [380, 0, 354, 0, 428, 0, 372, 0, 434, 0]]]

    flexCoinBalance = [[0 for x in range(_numHouses)] for y in range(numPeriods)]
    for j in range(0,_numHouses):
        _, flexCoinBalance[0][j] = FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[j])
    marketPrice = [RealTime.call().wholesalePrice() for x in range(0,numPeriods)]
    deviation = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [475, -294, -217, -294, -408, -450, -5, -499, -375, 429], [-431, 287, 35, -287, -229, -338, 197, -129, -435, -18], [41, 92, 129, -379, -81, 453, 54, 7, 299, 272], [-462, -56, -474, 118, -315, -360, 201, -443, 269, -41], [-292, -269, 437, -320, 318, -121, 101, 11, -413, -265], [164, -229, 144, -430, 455, -7, 357, -160, -232, 355], [-145, 94, 387, 13, -78, 0, 138, 243, -197, -25], [237, -368, 124, -497, -202, -5, -251, -27, -490, -417], [114, -149, 202, -76, 495, -265, 437, 356, 104, 79], [490, 450, -317, -393, -197, 95, -341, -43, -215, 118], [-412, 89, -226, 235, -330, -192, -466, -497, -21, -214], [-220, -214, -293, 298, -424, 47, 110, 354, 88, 287], [140, -448, 384, -164, 421, 180, 445, 266, 290, -122], [-52, 467, -75, 228, 362, 276, -354, 326, -58, 415], [-199, 234, 459, -368, -424, 217, -99, -253, 148, -66], [152, 319, -160, -207, -400, 356, 300, -336, -135, 117], [-369, -271, 18, -229, -361, 218, -493, -409, 301, -326], [-126, -469, 60, 2, 1, 36, 12, -204, -277, 298], [-324, 381, 4, 152, 478, 41, 49, -46, -231, -408]]

    for i in range(1, numPeriods): #144 for a whole day

        ### Setting the deviations
        for j in range(0,_numHouses):
            #deviation[i][j] = random.randint(-500, 500)
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

        ### Now, we must set the price based on the battery status
        # price[i] = setPrice(battery[i])

        ### Set the available flexibility in each battery
        availableFlex = setFlexibility(battery[i], batteryFlag)

        ### The trading happens, and the batteries are corrected for the trading
        battery[i], marketPrice[i], cost[i] = trade(price[i], battery[i], availableFlex, deviation[i])

        for j in range(0,_numHouses):
            if (battery[i][j] > battery[i - 1][j]):
                battery[i][j] = round(int(0.9 * battery[i][j]))
            _, flexCoinBalance[i][j] = FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[j])

    print(cost)
    #We must print the results!
    # The payment is amount of bid +/- transacted. What about the batteries and their deviation?
    return flexCoinBalance, battery, price, deviation, marketPrice, cost
flexCoinBalance, battery, price, deviation, marketPrice, cost = testRealTime()
