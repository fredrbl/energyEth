import "./FlexCoin.sol";

pragma solidity ^0.4.11;
contract Duration {

    struct Node {
        address owner;
        uint nodeID;
        uint numDemandHours;
        uint[] demandPrices;
        uint[] supplyHours;
    }

    uint public numNodes;
    mapping(uint => Node) public nodes;
 // Bueno. Que quiero hacer para manaña?
 1. probar la cosa sin y con seguridad
 2. Mostrar la asumpciones
 3. How simulate it? First 

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

    // Quiza la supply puede involver una variable que dice algo sobre la probilidad.
    // Por ejemplo; Un supply mas pronto deberia tiene un probilidad mas alto.
    // Que vas a hacer con lo? Combina alto prob aqui con alto prob abajo? hmm.

    function getNode(uint _nodeID, uint _timeStep) constant public returns(address, uint, uint, uint){
        return (nodes[_nodeID].owner, nodes[_nodeID].numDemandHours, nodes[_nodeID].demandPrices[_timeStep], nodes[_nodeID].supplyHours[_timeStep]);
    }


    function checkAndTransfer(uint[] sortedList, uint[] from, uint[] to, uint timeStep, address contractAddress) public returns(bool success) {
        // Because solidity not can receive two dimension list, we must call this for every time step
        FlexCoin f = FlexCoin(contractAddress);

        uint i = 0;
        if (sortedList.length > 1) {
        // Este puede ser equivocado! length puede dar length de un string/byte.
            for (i; i < (sortedList.length - 1); i++) {
                if (nodes[sortedList[i]].demandPrices[timeStep] > nodes[sortedList[i + 1]].demandPrices[timeStep]) { return false; }
                if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
                f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[sortedList[sortedList.length - 1]].demandPrices[timeStep]);
            }
        }
        if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
        f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[from[i]].demandPrices[timeStep]);
        //action for element when i => last element
    }
}
