#from web3 import Web3, HTTPProvider
import json
#import FlexCoin
import numpy as np

############### ASSUMPTIONS ###############
# This is a very simplified method. The following assumptions hold;
# - The loads must be available at all times (i.e a price between 1 -> 998)
# - The energy for one hour is always 1 kwh, both for supply and demand
# - The energy is always divided in one hour.
# - Each node is either a demand or supply node. A node cannot be both
# - That supp and demand is the same size => perfectly adequat.

#web3 = Web3(HTTPProvider('http://localhost:8545'))
#jsonFile = open('/home/fred/Documents/FlexCoin_dir/build/contracts.json', 'r')
#values = json.load(jsonFile)
#jsonFile.close()

#abi = values['Duration']['abi']
#address = input("What is the contract address? - FutureBlock: ")
#Duration = web3.eth.contract(address, abi = abi)

steps = 3
numNodes = 4

#tests

## demand is a [][] array from the blockchain
demandPrice = [[999 for t in range(0, steps)] for node in range(0, numNodes)]
demandHours = [0 for node in range(0,numNodes)]

supply = [[0 for t in range(0, steps)] for node in range(0, numNodes)]
# Supply is cuanto necesario en cada paso.

demandPrice[0] = [32, 31, 40] #Duration.call().getDemandPrice(node)
demandPrice[1] = [21, 32, 22]
demandHours[0] = 2 #Duration.call().getDemandHours(node)
demandHours[1] = 1
supply[2] = [1, 0, 1] #Duration.call().getSupply(node)
supply[3] = [1, 0, 0]

# getter for the demand y supply...!
for i in range(0,numNodes):
    owner[i], DemandHours[i], demandPrice[i], supply[i] = Duration.getNode(i)
demandPrice = (np.array(demandPrice)).transpose()
supply = (np.array(supply)).transpose()

def matching(supply, demand):
    sortedList = [[] for t in range(0, steps)]
    for t in range(0,steps):
        ## bueno. sort, y create a list of index equal to the list.
        for i in range(0, np.sum(supply[t])):
            sortedList[t].append(demandPrice[t].tolist().index(min(demandPrice[t])))
            demandPrice[t][sortedList[t][i]] = 999 # because a node not can give more in one step
            addressFrom = sortedList[t][i]
            addressTo = supply[t].tolist().index(1)
            supply[t][addressTo] = 0
            demandHours[sortedList[t][i]] = demandHours[sortedList[t][i]] - 1
            if (demandHours[sortedList[t][i]] == 0): # The demand node is empty, and must be set to 999
                for t2 in range(i, steps):
                    demandPrice[t2][sortedList[t][i]] = 999
            print(addressFrom)
            print(addressTo)
            print(demandHours)
        Duration.transact().checkAndTransfer(sortedList[t], addressFrom, addressTo, t, FlexCoin.address)

    return sortedList
