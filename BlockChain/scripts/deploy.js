async function main() {
    const FACEGUARD = await ethers.getContractFactory("FaceGuard");
 
    // Start deployment, returning a promise that resolves to a contract object
    const FACEGUARD_DEPLOYMENT = await FACEGUARD.deploy("Deployment User", "DeploymentUser123456789", "ThisUserRepresentsInitialContractDeployment.");
    console.log("Contract deployed to address:", FACEGUARD_DEPLOYMENT.address);
 }
 
 main()
   .then(() => process.exit(0))
   .catch(error => {
     console.error(error);
     process.exit(1);
   });