# energyEth

EnergyEth is a local energy market created in a Ethereum environment. This code here is suited for an environment which:
- Uses Populus to compile and deploy contracts
- Uses testRPC-py as blockchain
- Uses python to interact with the deployed smart contracts

## The folders
This repository exists of several folders. Below is a explanation of each folder, and how it is used in a blockchain environment

**MasterThesis:** This folder is a copy of the blockchain environment used in the master thesis written by Fredrik Blom. Title: "A Feasibility Study of Using Blockchain Technology As a Local Energy Market Infrastructure". This folder must hence not be changed, so that the results in the master thesis corresponds with the existing code that exists in this folder.  
**.cache:** Used for the testing environment in populus. Do not touch, and leave it be.  
**build:** When populus compiles the smart contract, it makes a build with the contract properties. It is necessary when the smart contracts are deployed on a blockchain  
**contracts:** The smart contracts are put here  
**python:** Python scripts are used in order to interact with the blockchain. This folder therefore contains all simulations and analysing tools to all contracts  
**tests:** This folder is used when testing the contracts  

## The contracts:
**Duration:** This is a duration differentiated method. In the thesis, this is called the _day ahead_ trading  
**DurationSecure:** This is the _day ahead_ trading without a security check in the smart contract  
**FlexCoin:** This is the payment contract. This creates houses and performs payments between the houses, independent on the trading mechanism  
**FutureBlock:** This is when the grid operator sells a future block of energy. It is called _load curtailment_ trading in the master thesis  
**RealTime:** This is the _real time_ trading in the master thesis  
**RealTimeCalculation:** This is the _real time_ trading in the master thesis  


## The other files in this repository:
populus.json: This is the file where all the blockchain network properties are stored. Examples is the mainnet for ethereum or a testRPC
