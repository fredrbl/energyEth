
from web3 import Web3, HTTPProvider
import json

web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/FlexCoin_dir/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['FlexCoin']['abi']
address = input("What is the contract address? - FlexCoin: ")
FlexCoin = web3.eth.contract(address, abi = abi)
numHouses = FlexCoin.call().numHouses()
if(numHouses == 0):
    for i in range(len(web3.personal.listAccounts)):
        FlexCoin.transact({'from': web3.eth.accounts[i]}).newHouse()


## This could also control the batteries!
## Now, this controls the money and batteries. If money changes, changes are made in bc
## If battery changes, the changes in the nodes are made here.
## other words => this is the main control center that ties all trading mechanisms together
## If the battery are changed in a time step, it must be reported to this instance.

# Now we have a vector for each house, where each element is the batteryPlan in one step.
batteryPlan = [[] for i in range(numHouses)]
