
from web3 import Web3, HTTPProvider
import json

## This function makes a house to each node in the system

web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/energyEth/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['FlexCoin']['abi']
address = input("What is the contract address? - FlexCoin: ")
FlexCoin = web3.eth.contract(address, abi = abi)
numHouses = FlexCoin.call().numHouses()
if(numHouses == 0):
    for i in range(len(web3.personal.listAccounts)):
        FlexCoin.transact({'from': web3.eth.accounts[i]}).newHouse()
