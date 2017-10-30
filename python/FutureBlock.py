
from web3 import Web3, HTTPProvider
import json
import FlexCoin

# Compile and deploy in populus in one terminal and testrpc-py in another
# Open a new terminal and rund this python script in python3
web3 = Web3(HTTPProvider('http://localhost:8545'))
jsonFile = open('/home/fred/Documents/FlexCoin_dir/build/contracts.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

abi = values['FutureBlock']['abi']
address = input("What is the contract address? - FutureBlock: ")
FutureBlock = web3.eth.contract(address, abi = abi)


####### Isolate and test the mechanism ###########
def testFutureBlock():
    FutureBlock.transact({'from': web3.eth.accounts[0]}).newOffer(15, 180)
    a = FutureBlock.call().numOffers()
    FutureBlock.transact({'from': web3.eth.accounts[1]}).setBid(a, 10, 40)
    FutureBlock.transact({'from': web3.eth.accounts[2]}).setBid(a, 5, 50)
    FutureBlock.transact({'from': web3.eth.accounts[3]}).setBid(a, 10, 30)
    FutureBlock.transact({'from': web3.eth.accounts[0]}).setAcceptedPrice(a, 30)
    FutureBlock.transact({'from': web3.eth.accounts[0]}).setAcceptedBids(a, 2)
    FutureBlock.transact().transferAndClose(a, FlexCoin.address)

    print(FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[0]))
    print(FlexCoin.FlexCoin.call().getHouse(web3.eth.accounts[3]))
