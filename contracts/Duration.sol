import "./FlexCoin.sol";

pragma solidity ^0.4.11;
contract Duration {

    struct Node {
        address owner;
        uint nodeID;
        uint numDemandHours;
        uint[3] demandPrices;
        uint[3] supplyHours;
    }

    uint public numNodes;
    mapping(uint => Node) public nodes;

    function setNode(uint _numDemandHours, uint[3] _demandPrices, uint[3] _supplyHours) public {
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

    function getNode(uint _nodeID) constant public returns(address, uint, uint[], uint[]){
        uint[] memory copyDemandPrices = new uint[](3);
        uint[] memory copySupplyHours = new uint[](3);

        copyDemandPrices[0] = nodes[_nodeID].demandPrices[0];
        copyDemandPrices[1] = nodes[_nodeID].demandPrices[1];
        copyDemandPrices[2] = nodes[_nodeID].demandPrices[2];
        copySupplyHours[0] = nodes[_nodeID].supplyHours[0];
        copySupplyHours[1] = nodes[_nodeID].supplyHours[1];
        copySupplyHours[2] = nodes[_nodeID].supplyHours[2];
        return (nodes[_nodeID].owner, nodes[_nodeID].numDemandHours, copyDemandPrices, copySupplyHours);
    }


    function checkAndTransfer(uint[] sortedList, uint[] from, uint[] to, uint timeStep, address contractAddress) public returns(bool success) {
        // Because solidity not can receive two dimension list, we must call this for every time step
        FlexCoin f = FlexCoin(contractAddress);

        FIX THE LENGTH...

        //uint i = 0;
        if (sortedList.length > 1) {
        // Este puede ser equivocado! length puede dar length de un string/byte.
            for (uint i = 0; i < (sortedList.length - 1); i++) {
                //if (nodes[sortedList[i]].demandPrices[timeStep] > nodes[sortedList[i + 1]].demandPrices[timeStep]) { return false; }
                //if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
                f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[sortedList[sortedList.length - 1]].demandPrices[timeStep]);
            }
            // Ahora, i es la numbero final. yo creo. quizas.
            //if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
            f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[from[i]].demandPrices[timeStep]);
            //action for element when i => last element
        }
    }
}
