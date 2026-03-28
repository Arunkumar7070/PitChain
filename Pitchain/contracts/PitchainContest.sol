// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PitchainContest
 * @dev Web3 IPL Fantasy Cricket contest manager on Base Sepolia
 *
 * Day 2 will flesh out full implementation.
 * This is the skeleton with all function signatures.
 */
contract PitchainContest {
    address public owner;
    uint256 public platformFeePercent = 5; // 5% platform fee

    struct Contest {
        uint256 id;
        uint256 entryFee;       // in wei
        uint256 prizePool;      // accumulated entry fees
        uint256 maxParticipants;
        uint256 participantCount;
        bool isActive;
        bool isPrizesDistributed;
    }

    mapping(uint256 => Contest) public contests;
    mapping(uint256 => mapping(address => bool)) public hasEntered;
    mapping(uint256 => address[]) public contestants;

    uint256 public contestCount;

    event ContestCreated(uint256 indexed contestId, uint256 entryFee, uint256 maxParticipants);
    event EntrySubmitted(uint256 indexed contestId, address indexed player, bytes32 teamHash);
    event PrizesDistributed(uint256 indexed contestId, address[] winners, uint256[] amounts);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function createContest(uint256 entryFee, uint256 maxParticipants) external onlyOwner returns (uint256) {
        contestCount++;
        contests[contestCount] = Contest({
            id: contestCount,
            entryFee: entryFee,
            prizePool: 0,
            maxParticipants: maxParticipants,
            participantCount: 0,
            isActive: true,
            isPrizesDistributed: false
        });
        emit ContestCreated(contestCount, entryFee, maxParticipants);
        return contestCount;
    }

    function joinContest(uint256 contestId, bytes32 teamHash) external payable {
        Contest storage c = contests[contestId];
        require(c.isActive, "Contest not active");
        require(!hasEntered[contestId][msg.sender], "Already entered");
        require(msg.value == c.entryFee, "Incorrect entry fee");
        require(c.participantCount < c.maxParticipants, "Contest full");

        hasEntered[contestId][msg.sender] = true;
        contestants[contestId].push(msg.sender);
        c.participantCount++;
        c.prizePool += msg.value;

        emit EntrySubmitted(contestId, msg.sender, teamHash);
    }

    function distributePrizes(
        uint256 contestId,
        address[] calldata winners,
        uint256[] calldata amounts
    ) external onlyOwner {
        Contest storage c = contests[contestId];
        require(!c.isPrizesDistributed, "Already distributed");
        require(winners.length == amounts.length, "Length mismatch");

        c.isPrizesDistributed = true;
        c.isActive = false;

        uint256 total = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            total += amounts[i];
        }
        require(total <= c.prizePool, "Exceeds prize pool");

        for (uint256 i = 0; i < winners.length; i++) {
            payable(winners[i]).transfer(amounts[i]);
        }

        // Platform fee to owner
        uint256 remaining = address(this).balance;
        if (remaining > 0) {
            payable(owner).transfer(remaining);
        }

        emit PrizesDistributed(contestId, winners, amounts);
    }

    function getContestants(uint256 contestId) external view returns (address[] memory) {
        return contestants[contestId];
    }

    receive() external payable {}
}
