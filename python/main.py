
# Followup after initialiseSystem
import copy
from web3 import Web3, HTTPProvider
import json
import random
import match
import time

# Compile and deploy in populus in one terminal and testrpc-py in another
# Open a new terminal and rund this python script in python3
web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/FlexCoin_dir/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()
abi = values['RealTime']['abi']
address = input("What is the contract address?")
FlexCoin = web3.eth.contract(address, abi = abi)


_numHouses = len(web3.personal.listAccounts)
wholesalePrice = 20
flexFlag = -1
transactions = [[] for y in range(3)]
upPrice = [[] for y in range(2)]
downPrice = [[] for y in range(2)]
upAvailableFlex = [[] for y in range(2)] # This is used if the system needs less consumption
downAvailableFlex = [[] for y in range(2)] # This is used if system needs more consumption
demand = [[] for y in range(2)]
supply = [[] for y in range(2)]


# Some houses have flexibility, and no deviation. Other houses have deviation, but no flex. Lets do 50/50
# This procedure is done by each house, so we might change this.
def trade() #input will be price and batteryplan for the spesific time step
    for i in range(0,_numHouses):
        FlexCoin.transact({'from': web3.eth.accounts[i]}).newHouse()
        if (i % 2 == 0):
            FlexCoin.transact().setHousePrice(i, random.randint(21,26), random.randint(14,19))
            FlexCoin.transact().setHouseBattery(i, random.randint(0,9), random.randint(0,8), 0)
        else:
            FlexCoin.transact().setHousePrice(i, random.randint(21,26), random.randint(14,19))
            FlexCoin.transact().setHouseBattery(i, 0, 0, random.randint(-9,9))

    for i in range(0,_numHouses):
        h = FlexCoin.call().getHouse(i)
        # Up means that the battery must sell energy -> upPrice > wholesalePrice
        upPrice[0].append(i)
        upPrice[1].append(h[0])
        downPrice[0].append(i)
        downPrice[1].append(h[1])
        upAvailableFlex[0].append(i)
        upAvailableFlex[1].append(h[2])
        downAvailableFlex[0].append(i)
        downAvailableFlex[1].append(h[3])
        if (h[4] < 0):
            demand[0].append(i)
            demand[1].append(-h[4])
        elif (h[4] > 0):
            supply[0].append(i)
            supply[1].append(h[4])

    print(upPrice)
    print(downPrice)
    print(upAvailableFlex)
    print(downAvailableFlex)
    print(demand)
    print(supply)

    ################################################################################
    ######## Here the initialisation should end, and other functions take over #####
    ################################################################################

    flexFlag, transactions, restEnergy = match.matching(flexFlag, transactions, demand, supply)

    if(sum(restEnergy[1]) == 0):  # This means that supply and demand cancel each other, and no more trading is necessary
        flexFlag = 2
        marketPrice = wholesalePrice

    price = [[0 for x in range(_numHouses)] for y in range(2)]
    copyPrice = [[0 for x in range(_numHouses)] for y in range(2)]

    # Sort los listas de precio
    # Mark that all prices only must consist of the nodes that is included in the trading

    i = 0
    print (flexFlag)
    if (flexFlag == 0):
        demandFlex = copy.deepcopy(upAvailableFlex)
        supplyFlex = restEnergy
        price = copy.deepcopy(upPrice)
        copyPrice = copy.deepcopy(upPrice)
        price[1] = sorted(price[1])
        for i in range(len(upPrice[1])):
            price[0][i] = copyPrice[0][copyPrice[1].index(price[1][i])]
            demandFlex[1][i] = upAvailableFlex[1][copyPrice[1].index(price[1][i])]
            demandFlex[0][i] = price[0][i]
            copyPrice[1][copyPrice[1].index(price[1][i])] = -1
    else:
        demandFlex = restEnergy
        supplyFlex = copy.deepcopy(downAvailableFlex)
        price = copy.deepcopy(downPrice)
        copyPrice = copy.deepcopy(downPrice)
        price[1] = sorted(price[1], reverse = True)
        for i in range(len(downPrice[1])):
            price[0][i] = copyPrice[0][copyPrice[1].index(price[1][i])]
            supplyFlex[1][i] = downAvailableFlex[1][copyPrice[1].index(price[1][i])]
            supplyFlex[0][i] = price[0][i]
            copyPrice[1][copyPrice[1].index(price[1][i])] = -1

    print(price)

    firstFlexFlag = copy.deepcopy(flexFlag)
    flexFlag, transactions, restEnergy = match.matching(flexFlag, transactions, demandFlex, supplyFlex)

    print(transactions)

    if (firstFlexFlag == 0):
        if(flexFlag == 0):
            wholesale = sum(restEnergy[1])
            marketPrice = wholesalePrice
            lastBattery = -1
            print("The system are still ",wholesale," kWh over the bid amount")
        else:
            lastBattery = transactions[1][len(transactions[0]) - 1]
            marketPrice = price[1][price[0].index(lastBattery)]
            print('The systems batteries can cover the deviations')
    elif(firstFlexFlag == 1):
        if(flexFlag == 0):
            lastBattery = transactions[0][len(transactions[0]) - 1]
            marketPrice = price[1][price[0].index(lastBattery)]
            print('The systems batteries can cover the deviations')
        else:
            wholesale = sum(restEnergy[1])
            marketPrice = wholesalePrice
            lastBattery = -1
            print("The system are still ",wholesale," kWh under the bid amount")

    ################################################################################
    ### The calculation is done, and the transactions are performed in blockchain ##
    ################################################################################

    FlexCoin.transact().checkAndTransactList(firstFlexFlag, price[0], price[1], transactions[0], transactions[1], transactions[2], marketPrice);
