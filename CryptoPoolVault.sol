// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CryptoPoolVault {
    struct Member {
        uint256 share;
        uint256 lastDeposit;
        bool active;
    }
    mapping(address => Member) public members;
    address[] public memberList;
    address public owner;
    uint256 public totalShares;
    uint256 public poolBalance;
    uint256 public lastBoostSpin;
    uint256 public boostMultiplier; // e.g., 250 = 2.5x
    uint256 public boostEnds;
    uint256 public constant BOOST_DURATION = 7 days;
    uint256 public constant BOOST_COOLDOWN = 14 days;
    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);
    event Trade(address indexed executor, uint256 amount, string details);
    event BoostSpin(address indexed host, uint256 multiplier);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    modifier onlyMember() {
        require(members[msg.sender].active, "Not a member");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function join() external {
        require(!members[msg.sender].active, "Already joined");
        members[msg.sender] = Member(0, 0, true);
        memberList.push(msg.sender);
    }

    function deposit() external payable onlyMember {
        require(msg.value > 0, "No value");
        members[msg.sender].share += msg.value;
        members[msg.sender].lastDeposit = block.timestamp;
        totalShares += msg.value;
        poolBalance += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external onlyMember {
        require(members[msg.sender].share >= amount, "Insufficient share");
        members[msg.sender].share -= amount;
        totalShares -= amount;
        poolBalance -= amount;
        payable(msg.sender).transfer(amount);
        emit Withdraw(msg.sender, amount);
    }

    function leave() external onlyMember {
        uint256 share = members[msg.sender].share;
        withdraw(share);
        members[msg.sender].active = false;
    }

    function executeTrade(uint256 amount, string calldata details) external onlyOwner {
        // Implement trade logic (DEX/CEX integration)
        emit Trade(msg.sender, amount, details);
    }

    function spinBoost() external onlyOwner {
        require(block.timestamp > lastBoostSpin + BOOST_COOLDOWN, "Boost cooldown");
        // Chainlink VRF or secure RNG should be used here
        uint256[] memory boosts = new uint256[](4);
        boosts[0] = 250; boosts[1] = 300; boosts[2] = 450; boosts[3] = 500;
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender, blockhash(block.number-1)))) % 4;
        boostMultiplier = boosts[rand];
        lastBoostSpin = block.timestamp;
        boostEnds = block.timestamp + BOOST_DURATION;
        emit BoostSpin(msg.sender, boostMultiplier);
    }

    function getBoostStatus() public view returns (uint256 multiplier, uint256 endsIn, uint256 cooldown) {
        multiplier = boostMultiplier;
        endsIn = boostEnds > block.timestamp ? boostEnds - block.timestamp : 0;
        cooldown = lastBoostSpin + BOOST_COOLDOWN > block.timestamp ? lastBoostSpin + BOOST_COOLDOWN - block.timestamp : 0;
    }

    function getMemberShare(address user) public view returns (uint256) {
        return members[user].share;
    }

    // Earnings split logic (equal/proportional) can be implemented here
    // Add ERC20 support, multi-sig, and security checks for production
} 