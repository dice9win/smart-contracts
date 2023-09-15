# Dice9 smart contracts

This repository contains Solidity source code of the smart contract used to run [dice9.win](https://dice9.win) - a tranparent, provably fair lottery-style game for EVM chains.

High-quality randomness generation is achieved by employing [RSA-FDH-VRF](https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-vrf-04#page-7) verifiable random function. The comments in [VRF.sol](https://github.com/dice9/smart-contracts/blob/main/contracts/VRF.sol) provide details of this process; a more formal writeup will be made available later.

 Contents of this repository are currently deployed at [0xD1CE9000dAe71a7130c193486761c324fbf94819](https://etherscan.io/address/0xd1ce9000dae71a7130c193486761c324fbf94819) on Ethereum mainnet. The contract at the [same address](https://bscscan.com/address/0xd1ce9000dae71a7130c193486761c324fbf94819) on Binance Smart Chain differs in parameters and RSA public key.

## Validating RSA permutation zero knowledge proof

Given properly generated modulus, RSA VRF is a permutation - each possible bet results in unique (as in one and only one) outcome, which excludes any possibility of unfair play by the House. To prove that RSA moduli employed by _dice9.win_ are always of that kind, a [non-interactive zero knowledge proof](https://en.wikipedia.org/wiki/Non-interactive_zero-knowledge_proof) is included in [the `Dice9.sol` comments](https://github.com/dice9win/smart-contracts/blob/main/contracts/Dice9.sol#L123-L131), computed according to the [paper by RSA-FDH-VRF authors](https://eprint.iacr.org/2018/057.pdf). In simple words, this proof consists of taking _random_ ciphertexts (obtained using [Fiat-Shamir transform](https://en.wikipedia.org/wiki/Fiat%E2%80%93Shamir_heuristic) to turn an interactive protocol into a non-interactive one) and providing corresponding plaintext - the paper proofs that this is infeasible to forge for a "bad" RSA modulus.

To verify this zero-knowledge proof, use a Python 3 script [proofcheck.py](https://github.com/dice9win/smart-contracts/blob/main/proofcheck.py) from this repository on a `Dice9.sol` file obtained from the verified contract in question from Etherscan/BscScan:
```shell
python3 proofcheck.py contracts/Dice9.sol
```
