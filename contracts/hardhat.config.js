require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  paths: {
    sources: "./contracts", // Changed from "./"
    cache: "./cache",
    artifacts: "./artifacts",
  },
  networks: {
    "0g_mainnet": {
      url: "https://evmrpc.0g.ai",
      accounts: process.env.DEPLOYER_PRIVATE_KEY
        ? [process.env.DEPLOYER_PRIVATE_KEY]
        : [],
      chainId: 16661,
    },
    "0g_testnet": {
      url: "https://evmrpc-testnet.0g.ai",
      accounts: process.env.DEPLOYER_PRIVATE_KEY
        ? [process.env.DEPLOYER_PRIVATE_KEY]
        : [],
      chainId: 16602,
    },
    u2u_mainnet: {
      url: "https://rpc-mainnet.u2u.xyz",
      accounts: process.env.DEPLOYER_PRIVATE_KEY
        ? [process.env.DEPLOYER_PRIVATE_KEY]
        : [],
      chainId: 39,
    },
    u2u_testnet: {
      url: "https://rpc-nebulas-testnet.uniultra.xyz",
      accounts: process.env.DEPLOYER_PRIVATE_KEY
        ? [process.env.DEPLOYER_PRIVATE_KEY]
        : [],
      chainId: 2484,
    },
  },
};
