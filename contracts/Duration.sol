import "./FlexCoin.sol"

pragma solidity ^0.4.11;
contract Duration {

    struct Node {
        address owner;
        uint nodeID;
        uint numDemandHours;
        uint[] demandPrices;
        bool[] supplyHours;
    }

    steps = 24; // nr of time steps
    uint numNodes;
    mapping(uint => Node) public nodes

    function setNode(uint _numDemandHours, uint[] _demandPrices, bool[] _supplyHours) public {
        numNodes = numNodes + 1;
        Node n = nodes[numNodes];
        n.owner = msg.sender;
        n.nodeID = numNodes;
        n.numDemandHours = _numDemandHours;
        n.demandPrices = _demandPrices;
        n.supplyHours = _supplyHours;
        // si no functiona con array como ingreso, pone un uint 01010111000.
    }
    // Quiza la supply puede involver una variable que dice algo sobre la probilidad.
    // Por ejemplo; Un supply mas pronto deberia tiene un probilidad mas alto.
    // Que vas a hacer con lo? Combina alto prob aqui con alto prob abajo? hmm.

    function getNode()


    function checkAndTransfer(uint[] sortedList, uint[] from, uint[] to, uint timeStep, address contractAddress) public {
        // Because solidity not can receive two dimension list, we must call this for every time step
        FlexCoin f = FlexCoin(contractAddress)
        memory uint counter = 0;
        uint i = 0;
        if (sortedList.length > 1) {
        // Este puede ser equivocado! length puede dar length de un string/byte.
            for (i; i < (sortedList.length - 1); i++) {
                memory uint[] _supplyHours = nodes[to[i]].supplyHours[timeStep];
                if (nodes[sortedList[i]].demandPrice[timeStep] > nodes[sortedList[i + 1]].demandPrice[timeStep]) { return false; }
                if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
                f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[sortedList[sortedList.length]].demandPrice[timeStep]);
            }
            // Ahora, i es la numbero final. yo creo. quizas.
            if (from[i] != nodes[sortedList[i]].nodeID || nodes[to[i]].supplyHours[timeStep] == 0) { return false; }
            f.transferHouse(nodes[from[i]].owner, nodes[to[i]].owner, nodes[from[i]].demandPrice[timeStep]);
            //action for element when i => last element
        }
    }
}
