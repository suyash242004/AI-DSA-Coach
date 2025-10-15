import json
import time
from web3 import Web3
from pathlib import Path
import streamlit as st
from typing import Optional, Dict, Any

# Global variables
w3 = None
nft_contract = None
token_contract = None

class Web3Client:
    def __init__(self):
        self.w3 = None
        self.nft_contract = None
        self.token_contract = None
        self.initialized = False
        
    def initialize(self):
        """Initialize Web3 connection to U2U mainnet"""
        try:
            # U2U Mainnet RPC - you'll get this from HackQuest
            rpc_url = st.secrets.get("U2U_RPC", "https://rpc-mainnet.u2u.xyz")
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.w3.is_connected():
                st.error("Failed to connect to U2U network")
                return False
                
            # Load contract addresses from secrets
            nft_address = st.secrets.get("NFT_CONTRACT_ADDRESS")
            token_address = st.secrets.get("DSA_TOKEN_CONTRACT_ADDRESS")
            
            # Load ABIs
            nft_abi = self._load_abi("DSABadge_abi.json")
            token_abi = self._load_abi("DSAToken_abi.json")
            
            if nft_address and nft_abi:
                self.nft_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(nft_address),
                    abi=nft_abi
                )
                
            if token_address and token_abi:
                self.token_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(token_address),
                    abi=token_abi
                )
                
            self.initialized = True
            return True
            
        except Exception as e:
            st.error(f"Web3 initialization failed: {e}")
            return False
    
    def _load_abi(self, filename: str) -> Optional[list]:
        """Load contract ABI from data directory"""
        try:
            abi_path = Path(f"data/{filename}")
            if abi_path.exists():
                with open(abi_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Failed to load ABI {filename}: {e}")
        return None
    
    def get_deployer_account(self):
        """Get deployer account from private key"""
        try:
            private_key = st.secrets.get("DEPLOYER_PRIVATE_KEY")
            if not private_key:
                raise ValueError("DEPLOYER_PRIVATE_KEY not found in secrets")
            return self.w3.eth.account.from_key(private_key)
        except Exception as e:
            st.error(f"Failed to load deployer account: {e}")
            return None
    
    def mint_nft_badge(self, user_address: str, problem_title: str, difficulty: str) -> Optional[str]:
        """Mint NFT badge for completing a problem"""
        if not self.initialized or not self.nft_contract:
            return None
            
        try:
            deployer = self.get_deployer_account()
            if not deployer:
                return None
                
            # Create metadata for the NFT
            token_uri = self._create_token_uri(problem_title, difficulty)
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(deployer.address)
            transaction = self.nft_contract.functions.mintBadge(
                Web3.to_checksum_address(user_address),
                token_uri
            ).build_transaction({
                'from': deployer.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, deployer.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                return tx_hash.hex()
            else:
                st.error("NFT minting transaction failed")
                return None
                
        except Exception as e:
            st.error(f"NFT minting failed: {e}")
            return None
    
    def transfer_dsa_tokens(self, user_address: str, amount: int) -> Optional[str]:
        """Transfer DSA tokens to user"""
        if not self.initialized or not self.token_contract:
            return None
            
        try:
            deployer = self.get_deployer_account()
            if not deployer:
                return None
                
            # Convert to token units (assuming 18 decimals)
            token_amount = amount * (10 ** 18)
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(deployer.address)
            transaction = self.token_contract.functions.transfer(
                Web3.to_checksum_address(user_address),
                token_amount
            ).build_transaction({
                'from': deployer.address,
                'nonce': nonce,
                'gas': 100000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, deployer.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                return tx_hash.hex()
            else:
                st.error("Token transfer transaction failed")
                return None
                
        except Exception as e:
            st.error(f"Token transfer failed: {e}")
            return None
    
    def get_user_token_balance(self, user_address: str) -> int:
        """Get user's DSA token balance"""
        if not self.initialized or not self.token_contract:
            return 0
            
        try:
            balance_wei = self.token_contract.functions.balanceOf(
                Web3.to_checksum_address(user_address)
            ).call()
            # Convert from wei to tokens (assuming 18 decimals)
            return balance_wei // (10 ** 18)
        except Exception as e:
            st.error(f"Failed to get token balance: {e}")
            return 0
    
    def get_user_nft_count(self, user_address: str) -> int:
        """Get number of NFT badges owned by user"""
        if not self.initialized or not self.nft_contract:
            return 0
            
        try:
            return self.nft_contract.functions.balanceOf(
                Web3.to_checksum_address(user_address)
            ).call()
        except Exception as e:
            st.error(f"Failed to get NFT count: {e}")
            return 0
    
    def _create_token_uri(self, problem_title: str, difficulty: str) -> str:
        """Create metadata URI for NFT"""
        metadata = {
            "name": f"DSA Badge - {problem_title}",
            "description": f"Completed {difficulty} level DSA problem: {problem_title}",
            "image": f"https://your-metadata-server.com/badges/{difficulty.lower()}.png",
            "attributes": [
                {"trait_type": "Problem", "value": problem_title},
                {"trait_type": "Difficulty", "value": difficulty},
                {"trait_type": "Platform", "value": "AI DSA Coach"},
                {"trait_type": "Timestamp", "value": int(time.time())}
            ]
        }
        
        # In production, you'd upload this to IPFS and return the IPFS URL
        # For now, return a placeholder
        return f"https://your-metadata-server.com/metadata/{problem_title.replace(' ', '_')}.json"
    
    def verify_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Verify transaction status"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                "success": receipt.status == 1,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "transaction_hash": tx_hash
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global instance
web3_client = Web3Client()