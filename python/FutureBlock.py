
from web3 import Web3, HTTPProvider
import json
import FlexCoin

# Compile and deploy in populus in one terminal and testrpc-py in another
# Open a new terminal and rund this python script in python3
web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/energyEth/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['FutureBlock']['abi']
address = input("What is the contract address? - FutureBlock: ")
FutureBlock = web3.eth.contract(address, abi = abi)
cost = 0

####### Isolate and test the mechanism ###########
def testFutureBlock():
    tempCost = []
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[0]}).newOffer(15, 150, 180))
    a = FutureBlock.call().numOffers()
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[1]}).setBid(a, 10, 40))
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[2]}).setBid(a, 5, 50))
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[3]}).setBid(a, 10, 30))
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[1]}).updateBid(a, 0, 19, 29))
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[0]}).setAcceptedPrice(a, 30))
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[0]}).setAcceptedBids(a, 2))
    tempCost.append(FutureBlock.transact({'from': web3.eth.accounts[0]}).setAcceptedBids(a, 1))
    tempCost.append(FutureBlock.transact().transferAndClose(a, FlexCoin.address))
    for i in range(0,len(tempCost)):
        tempCost[i] = web3.eth.getTransactionReceipt(tempCost[i]).gasUsed

    return tempCost

Costs = testFutureBlock()
