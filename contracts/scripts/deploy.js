const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying AI DSA Coach contracts to 0G Testnet...");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", balance.toString(), "wei");

  // Deploy DSA Token
  console.log("\nDeploying DSA Token...");
  const DSAToken = await ethers.getContractFactory("DSAToken");
  const dsaToken = await DSAToken.deploy();
  await dsaToken.waitForDeployment();
  const dsaTokenAddress = await dsaToken.getAddress();
  console.log("DSA Token deployed to:", dsaTokenAddress);

  // Deploy DSA Badge NFT
  console.log("\nDeploying DSA Badge NFT...");
  const DSABadge = await ethers.getContractFactory("DSABadge");
  const dsaBadge = await DSABadge.deploy();
  await dsaBadge.waitForDeployment();
  const dsaBadgeAddress = await dsaBadge.getAddress();
  console.log("DSA Badge NFT deployed to:", dsaBadgeAddress);

  // Save deployment info
  const deploymentInfo = {
    network: "0g_testnet",
    chainId: 16602,
    DSAToken: dsaTokenAddress,
    DSABadge: dsaBadgeAddress,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
    blockNumber: await ethers.provider.getBlockNumber(),
  };

  // Save to contracts directory
  fs.writeFileSync(
    path.join(__dirname, "../deployment.json"),
    JSON.stringify(deploymentInfo, null, 2)
  );

  // Save ABIs to data directory (for frontend)
  const dataDir = path.join(__dirname, "../../data");
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  // Get contract artifacts and save ABIs
  const DSATokenArtifact = await artifacts.readArtifact("DSAToken");
  const DSABadgeArtifact = await artifacts.readArtifact("DSABadge");

  fs.writeFileSync(
    path.join(dataDir, "DSAToken_abi.json"),
    JSON.stringify(DSATokenArtifact.abi, null, 2)
  );

  fs.writeFileSync(
    path.join(dataDir, "DSABadge_abi.json"),
    JSON.stringify(DSABadgeArtifact.abi, null, 2)
  );

  console.log("\n=== DEPLOYMENT COMPLETE ===");
  console.log("DSA Token:", dsaTokenAddress);
  console.log("DSA Badge:", dsaBadgeAddress);
  console.log("Explorer:", `https://chainscan-newton.0g.ai/address/${dsaTokenAddress}`);
  console.log("ABIs saved to data/ directory");

  console.log("\n=== UPDATE YOUR SECRETS ===");
  console.log("Add these to .streamlit/secrets.toml:");
  console.log(`DSA_TOKEN_CONTRACT_ADDRESS = "${dsaTokenAddress}"`);
  console.log(`NFT_CONTRACT_ADDRESS = "${dsaBadgeAddress}"`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
