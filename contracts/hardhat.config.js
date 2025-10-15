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
