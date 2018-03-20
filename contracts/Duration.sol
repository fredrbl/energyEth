import "./FlexCoin.sol";

pragma solidity ^0.4.11;
contract Duration {

    struct Node {
        address owner;
        uint nodeID;
        uint numDemandHours;
        string demandPrices;
        string supplyHours;
    }

    uint public numNodes;
    mapping(uint => Node) public nodes;

    function setNode(uint _numDemandHours, string _demandPrices, string _supplyHours) public {
        Node n = nodes[numNodes];
        n.owner = msg.sender;
        n.nodeID = numNodes;
        n.numDemandHours = _numDemandHours;
        n.demandPrices = _demandPrices;
        n.supplyHours = _supplyHours;
        numNodes = numNodes + 1;
    }
    // gas cost: 206 205

    function getNode(uint _nodeID) constant public returns(address, uint, string, string){
        return (nodes[_nodeID].owner, nodes[_nodeID].numDemandHours, nodes[_nodeID].demandPrices, nodes[_nodeID].supplyHours);
    }

    function checkAndTransfer(uint[] sortedList, uint[] from, uint[] to, uint[] price, uint timeStep, address contractAddress) public returns(bool success) {
        // Because solidity not can receive two dimension list, we must call this for every time step
        FlexCoin f = FlexCoin(contractAddress);

        uint i = 0;
        if (sortedList.length > 1) {
            for (i; i < (sortedList.length - 1); i++) {
                f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, price[from[i]]);
            }
        }
        f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, price[from[i]]);
    }
    // gas cost: 59033
}
