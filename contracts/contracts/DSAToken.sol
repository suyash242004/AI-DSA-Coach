// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title DSAToken
 * @dev ERC20 token for DSA learning rewards
 */
contract DSAToken is ERC20, Ownable {
    
    // Token distribution events
    event TokensAwarded(address indexed user, uint256 amount, string reason);
    event TokensConverted(address indexed user, uint256 dsaAmount, uint256 usdcAmount);
    
    // Token economics
    mapping(address => uint256) public totalEarned;
    mapping(address => uint256) public problemsSolved;
    mapping(address => uint256) public lastLoginTime;
    mapping(address => uint256) public loginStreak;
    
    // Conversion rate: 100 DSA = 1 USDC (in wei, assuming USDC has 6 decimals)
    uint256 public constant CONVERSION_RATE = 100;
    
    constructor() ERC20("DSA Coin", "DSA") {
        // Mint initial supply to owner (10 million tokens)
        _mint(msg.sender, 10_000_000 * 10**18);
    }
    
    /**
     * @dev Award tokens to user for completing problems
     */
    function awardTokens(address user, uint256 amount, string memory reason) public onlyOwner {
        _mint(user, amount * 10**18); // Convert to wei
        totalEarned[user] += amount;
        
        emit TokensAwarded(user, amount, reason);
    }
    
    /**
     * @dev Award daily login bonus
     */
    function awardDailyBonus(address user) public onlyOwner {
        uint256 lastLogin = lastLoginTime[user];
        uint256 currentTime = block.timestamp;
        
        // Check if it's a new day (86400 seconds = 1 day)
        if (currentTime - lastLogin >= 86400) {
            // Award 1 token for daily login
            _mint(user, 1 * 10**18);
            totalEarned[user] += 1;
            
            // Update streak
            if (currentTime - lastLogin <= 172800) { // Within 2 days
                loginStreak[user] += 1;
            } else {
                loginStreak[user] = 1; // Reset streak
            }
            
            lastLoginTime[user] = currentTime;
            
            // Bonus for streaks
            if (loginStreak[user] == 7) {
                _mint(user, 5 * 10**18); // 5 token bonus for 7-day streak
                totalEarned[user] += 5;
                emit TokensAwarded(user, 5, "7-day login streak bonus");
            } else if (loginStreak[user] == 30) {
                _mint(user, 15 * 10**18); // 15 token bonus for 30-day streak
                totalEarned[user] += 15;
                emit TokensAwarded(user, 15, "30-day login streak bonus");
            }
            
            emit TokensAwarded(user, 1, "Daily login bonus");
        }
    }
    
    /**
     * @dev Record problem completion
     */
    function recordProblemCompletion(address user, string memory difficulty) public onlyOwner {
        problemsSolved[user] += 1;
        
        // Award tokens based on difficulty
        uint256 reward;
        if (keccak256(bytes(difficulty)) == keccak256(bytes("Easy"))) {
            reward = 1;
        } else if (keccak256(bytes(difficulty)) == keccak256(bytes("Medium"))) {
            reward = 2;
        } else if (keccak256(bytes(difficulty)) == keccak256(bytes("Hard"))) {
            reward = 3;
        }
        
        if (reward > 0) {
            _mint(user, reward * 10**18);
            totalEarned[user] += reward;
            
            string memory reason = string(abi.encodePacked("Solved ", difficulty, " problem"));
            emit TokensAwarded(user, reward, reason);
        }
    }
    
    /**
     * @dev Get user statistics
     */
    function getUserStats(address user) public view returns (
        uint256 balance,
        uint256 earned,
        uint256 solved,
        uint256 streak
    ) {
        balance = balanceOf(user) / 10**18; // Convert from wei
        earned = totalEarned[user];
        solved = problemsSolved[user];
        streak = loginStreak[user];
    }
    
    /**
     * @dev Convert DSA tokens to USDC (placeholder)
     * In production, this would interface with a USDC contract
     */
    function convertToUSDC(uint256 dsaAmount) public {
        require(dsaAmount >= CONVERSION_RATE, "Minimum 100 DSA required for conversion");
        require(balanceOf(msg.sender) >= dsaAmount * 10**18, "Insufficient DSA balance");
        
        // Burn DSA tokens
        _burn(msg.sender, dsaAmount * 10**18);
        
        // Calculate USDC amount (1% of DSA amount, representing 100:1 ratio)
        uint256 usdcAmount = dsaAmount / CONVERSION_RATE;
        
        // In production, mint USDC or transfer from reserve
        // For now, just emit event
        emit TokensConverted(msg.sender, dsaAmount, usdcAmount);
    }
    
    /**
     * @dev Batch award tokens to multiple users
     */
    function batchAwardTokens(
        address[] memory users,
        uint256[] memory amounts,
        string memory reason
    ) public onlyOwner {
        require(users.length == amounts.length, "Arrays length mismatch");
        
        for (uint256 i = 0; i < users.length; i++) {
            _mint(users[i], amounts[i] * 10**18);
            totalEarned[users[i]] += amounts[i];
            emit TokensAwarded(users[i], amounts[i], reason);
        }
    }
}