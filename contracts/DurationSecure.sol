
import "./FlexCoin.sol";

pragma solidity ^0.4.11;
contract DurationSecure {

    struct Node {
        address owner;
        uint nodeID;
        uint numDemandHours;
        uint[] demandPrices;
        uint[] supplyHours;
    }

    uint public numNodes;
    mapping(uint => Node) public nodes;

    function setNode(uint _numDemandHours, uint[] _demandPrices, uint[] _supplyHours) public {
        Node n = nodes[numNodes];
        n.owner = msg.sender;
        n.nodeID = numNodes;
        n.numDemandHours = _numDemandHours;
        n.demandPrices = _demandPrices;
        n.supplyHours = _supplyHours;
        numNodes = numNodes + 1;
        // si no functiona con array como ingreso, pone un uint 01010111000.
    }
    // 206 205 gas

    // Quiza la supply puede involver una variable que dice algo sobre la probilidad.
    // Por ejemplo; Un supply mas pronto deberia tiene un probilidad mas alto.
    // Que vas a hacer con lo? Combina alto prob aqui con alto prob abajo? hmm.

    function getNode(uint _nodeID, uint timeStep, uint nodeFlag) constant public returns(address, uint, uint, uint){
        if (nodeFlag == 0){ // Here, the node is a supply node
            return (nodes[_nodeID].owner, nodes[_nodeID].numDemandHours, nodes[_nodeID].demandPrices[0], nodes[_nodeID].supplyHours[timeStep]);
        }
        else {
            return (nodes[_nodeID].owner, nodes[_nodeID].numDemandHours, nodes[_nodeID].demandPrices[timeStep], nodes[_nodeID].supplyHours[0]);
        }
    }

    function checkAndTransfer(uint[] sortedList, uint[] from, uint[] to, uint timeStep, address contractAddress) public returns(bool success) {
        // Because solidity not can receive two dimension list, we must call this for every time step
        FlexCoin f = FlexCoin(contractAddress);

        uint i = 0;
        if (sortedList.length > 1) {
        // Este puede ser equivocado! length puede dar length de un string/byte.
        ALSO! CHECK THAT THE PRICES FROM THE CHOSEN NODES ARE LOWER/HIGHER THAN THE CLEARING PRICE!
            for (i; i < (sortedList.length - 1); i++) {
                if (nodes[sortedList[i]].demandPrices[timeStep] > nodes[sortedList[i + 1]].demandPrices[timeStep]) { return false; }
                if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
                f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[sortedList[sortedList.length - 1]].demandPrices[timeStep]);
            }
<<<<<<< HEAD
        }S
        if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
=======
        }
<<<<<<< HEAD
        if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
=======
        //if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
>>>>>>> 82693dd75746db0f01e09b37a0660bb8ec2b9cc2
>>>>>>> 3e18799ebabde16f814a53b4235f07daff4a7f37
        f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[from[i]].demandPrices[timeStep]);
        //action for element when i => last element
    }
    // 62 551 gas
}
