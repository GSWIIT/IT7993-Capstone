async function main() {
    const FACEGUARD = await ethers.getContractFactory("FaceGuard");
 
    // Start deployment, returning a promise that resolves to a contract object
    const FACEGUARD_DEPLOYMENT = await FACEGUARD.deploy();
    console.log(FACEGUARD_DEPLOYMENT.address);
 }
 
 main()
   .then(() => process.exit(0))
   .catch(error => {
     console.error(error);
     process.exit(1);
   });