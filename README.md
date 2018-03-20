# energyEth

Several local energy market mechanisms built in a Ethereum environment. Purpose is to use Ethereum as infrastructure for a local energy market.
- Populus is used to generate the default blockchain environment.

## The archives
MasterThesis: This archive is a copy of the blockchain environment used in the master thesis written by Fredrik Blom. Title: "A Feasibility Study of Using Blockchain Technology As a Local Energy Market Infrastructure". This archive must hence not be changed, so that the results in the master thesis corresponds with the existing code that exists in this archive.

.cache: Used for the testing environment in populus. Do not touch, and leave it be.

build: When populus compiles the smart contract, it makes a build with the contract properties. It is necessary when the smart contracts are deployed on a blockchain

contracts: The smart contracts are put here

python: Python scripts are used in order to interact with the blockchain. This archive therefore contains all simulations and analysing tools to all contracts

tests: This archive is used when testing the contracts 

## The three trading mechanisms:
Duration: This is a duration differentiated method. In the thesis, this is called the day ahead trading
RealTime: This is the real time trading
FutureBlock: This is when the grid operator sells a future block of energy. It is called


## The other files in this repository:
populus.json: This is the file where all the blockchain network properties are stored. Examples is the mainnet for ethereum or a testRPC
