# energyEth

EnergyEth is a local energy market created in a Ethereum environment. This code here is suited for an environment which:
- Uses Populus to compile and deploy contracts
- Uses testRPC-py as blockchain
- Uses python to interact with the deployed smart contracts

## The folders
This repository exists of several folders. Below is a explanation of each folder, and how it is used in a blockchain environment

- **MasterThesis:** This folder is a copy of the blockchain environment used in the master thesis written by Fredrik Blom. Title: "A Feasibility Study of Using Blockchain Technology As a Local Energy Market Infrastructure". This folder must hence not be changed, so that the results in the master thesis corresponds with the existing code that exists in this folder.
- **.cache:** Used for the testing environment in populus. Do not touch, and leave it be.
- **build:** When populus compiles the smart contract, it makes a build with the contract properties. It is necessary when the smart contracts are deployed on a blockchain
- **contracts:** The smart contracts are put here  
- **python:** Python scripts are used in order to interact with the blockchain. This folder therefore contains all simulations and analysing tools to all contracts
- **tests:** This folder is used when testing the contracts
- **populus.json**: This is the file where all the blockchain network properties are stored. Examples is the mainnet for ethereum or a testRPC

## The contracts:
- **Duration:** This is a duration differentiated method. In the thesis, this is called the _day ahead_ trading
- **DurationSecure:** This is the _day ahead_ trading without a security check in the smart contract
- **FlexCoin:** This is the payment contract. This creates houses and performs payments between the houses, independent on the trading mechanism
- **FutureBlock:** This is when the grid operator sells a future block of energy. It is called _load curtailment_ trading in the master thesis
- **RealTime:** This is the _real time_ trading in the master thesis
- **RealTimeCalculation:** This is the _real time_ trading in the master thesis

## Dependencies:
Note that the following dependencies do depend on other dependencies. The used operating system for the master thesis was Linux Lubuntu 16.04. Linux is recommended as operating system, as the author did not manage to run the environment on windows.

- Populus
- TestRPC-py must be installed and have its properties in populus.json
- Python 3

## How to simulate
In order to simulate the environment, the python script must be specialised to the respective path where the folder is put. The following assumes that all dependencies are installed succsessfully.

1. Open a terminal window and run TestRPC-py
1. Open another terminal window, and go to the directory ~/energyEth. In this window, do these two steps:
    1. Compile the smart contracts using populus. This is done by `$ populus compile`
    1. If successful, deploy the contracts on the blockchain. This is done by `$ populus deploy --chain 'local' --no-wait-for-sync`
1. Open a third terminal window, and start python 3. Here you can run the python scripts found in the folder pyhton in this repository
