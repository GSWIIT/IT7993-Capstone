/** @type import('hardhat/config').HardhatUserConfig */

require("dotenv").config(); // Use environment variables for security
require("@nomiclabs/hardhat-ethers");

const { API_URL, PRIVATE_KEY } = process.env;

module.exports = {
  solidity: "0.8.0",
  networks: {
    sepolia: {
      url: API_URL, // Set this in your .env file
      accounts: [`0x${PRIVATE_KEY}`], // Your wallet private key
    },
  },
};
