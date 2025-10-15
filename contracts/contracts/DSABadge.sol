

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DSABadge is ERC721, ERC721URIStorage, Ownable {
    
    uint256 private _tokenIdCounter;
    
    // Mapping from user address to array of earned badges
    mapping(address => uint256[]) public userBadges;
    
    // Badge metadata
    struct Badge {
        string problemTitle;
        string difficulty;
        uint256 timestamp;
        address earner;
    }
    
    mapping(uint256 => Badge) public badges;
    
    event BadgeMinted(address indexed user, uint256 indexed tokenId, string problemTitle, string difficulty);
    
    constructor() ERC721("DSA Achievement Badge", "DSABADGE") {}
    
    function mintBadge(
        address to,
        string memory problemTitle,
        string memory difficulty,
        string memory uri
    ) public onlyOwner {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        
        badges[tokenId] = Badge({
            problemTitle: problemTitle,
            difficulty: difficulty,
            timestamp: block.timestamp,
            earner: to
        });
        
        userBadges[to].push(tokenId);
        
        emit BadgeMinted(to, tokenId, problemTitle, difficulty);
    }
    
    function getUserBadges(address user) public view returns (uint256[] memory) {
        return userBadges[user];
    }
    
    function getBadgeDetails(uint256 tokenId) public view returns (Badge memory) {
        require(_exists(tokenId), "Badge does not exist");
        return badges[tokenId];
    }
    
    function getTotalBadges() public view returns (uint256) {
        return _tokenIdCounter;
    }
    
    // Required overrides
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}