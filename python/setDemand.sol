




contract dayAhead {

    struct Demand {
        address sender;
        uint amount;
        uint price;
    }

    mapping(uint => Demand) demandBids;
    uint public numDemandBids;

    function newDemand(uint _amount, uint _price) public {
        numDemandBids = numDemandBids + 1;
        uint demandID = numDemandBids;
        Demand d = demandBids[demandID];
        d.sender = msg.sender;
        d.amount = _amount;
        d.price = _price;
    }
    // gas usage = 37 622
}

contract NordPoolUser {

    struct User {
        address owner;
        uint flexCoinBalance;
    }

    mapping(uint => User) users;
    uint public numUsers;

    function newUser() public {
        numUsers = numUsers + 1;
        User u = users[userID];
        h.owner = msg.sender;
        h.flexCoinBalance = 2 000;
    }
}
