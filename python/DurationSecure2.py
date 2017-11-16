from web3 import Web3, HTTPProvider
import json
import FlexCoin
import numpy as np

############### ASSUMPTIONS ###############
# This is a very simplified method. The following assumptions hold;
# - The loads must be available at all times (i.e a price between 1 -> 998)
# - The energy for one hour is always 1 kwh, both for supply and demand
# - The energy is always divided in one hour.
# - Each node is either a demand or supply node. A node cannot be both
# - That supp and demand is the same size => perfectly adequat.


### SIMULATION ###
# - Set in a profile with solar and wind prod.
# - A market where the demand is moved. This does not necessarily affect the batteries.
# - Basically. Start with only supply and demand for one day. In this market, everything
# has to be dealed with inside of the microgrid. The dem+supp is set, and the rest of the day is steered with deviations.


web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/energyEth/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['DurationSecure2']['abi']
address = input("What is the contract address? - DurationSecure2: ")
Duration = web3.eth.contract(address, abi = abi)

steps = 3
numNodes = 4

## demand is a [][] array from the blockchain
#demandPrice = [[999 for t in range(0, steps)] for node in range(0, numNodes)]
#demandHours = [0 for node in range(0,numNodes)]

#supplyHours = [[0 for t in range(0, steps)] for node in range(0, numNodes)]
# supplyHours is cuanto necesario en cada paso.

#demandPrice[0] = [32, 31, 40] #Duration.call().getDemandPrice(node)
#demandPrice[1] = [21, 32, 22]
#demandHours[0] = 2 #Duration.call().getDemandHours(node)
#demandHours[1] = 1
#supplyHours[2] = [1, 0, 1] #Duration.call().getsupplyHours(node)
#supplyHours[3] = [1, 0, 0]

owner = ["0" for i in range(0, numNodes)]
demandHours = [0 for i in range(0, numNodes)]
demandPrices = [[0 for x in range(0, steps)] for y in range(0, numNodes)]
supplyHours = [[0 for x in range(0, steps)] for y in range(0, numNodes)]
# getter for the demand y supplyHours...!
for i in range(0,numNodes):
    if (i == 0):
        Duration.transact({'from': web3.eth.accounts[i]}).setNode(2, [32, 21, 43], [0, 0, 0])
    elif(i == 1):
        Duration.transact({'from': web3.eth.accounts[i]}).setNode(1, [15, 19, 60], [0, 0, 0])
    elif(i == 2):
        Duration.transact({'from': web3.eth.accounts[i]}).setNode(0, [999, 999, 999], [1, 0, 1])
    elif(i == 3):
        Duration.transact({'from': web3.eth.accounts[i]}).setNode(0, [999, 999, 999], [1, 0, 0])
    for t in range(0, steps):
        owner[i], demandHours[i], demandPrices[i][t], supplyHours[i][t] = Duration.call().getNode(i, t)
demandPrices = (np.array(demandPrices)).transpose()
supplyHours = (np.array(supplyHours)).transpose()

def matching(supplyHours, demandPrices):
    sortedList = [[] for t in range(0, steps)]
    addressFrom = [[] for t in range(0, steps)]
    addressTo = [[] for t in range(0, steps)]
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
        print(addressFrom)
        print(addressTo)
        print(sortedList[t])
        if(len(sortedList[t]) > 0):
            Duration.transact().checkAndTransfer(sortedList[t], addressFrom[t], addressTo[t], t, FlexCoin.address)
        print(FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[1]))
        print(FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[2]))
    return sortedList

matching(supplyHours, demandPrices)
