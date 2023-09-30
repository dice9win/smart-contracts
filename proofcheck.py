import re
import sys
import argparse
import hashlib
import base64

parser = argparse.ArgumentParser(
    prog="proofcheck",
    description="validate the zero knowledge proof of RSA modulus being a permutation")

parser.add_argument("contract_sol", metavar="Dice9.sol")

args = parser.parse_args()

# read the contract
with open(args.contract_sol, "r") as fi:
    contract = fi.read()

# collect modulus lines
modulus_line = re.compile(r"internal\s+MODULUS(?P<evm_word_index>\d)\s+=\s+(?P<evm_word>0x[0-9A-Fa-f]+);")
modulus = sum([2**(256*(3-int(m['evm_word_index']))) * int(m['evm_word'], 16)
               for m in modulus_line.finditer(contract, re.MULTILINE)])

# collect nizk proof responses
nizk_line = re.compile(r"nizk:(?P<nizk_iters>\d+):(?P<iter>\d+):(?P<subiter>\d+):(?P<challenge_response>[^=]+==)")
responses = [(int(m['nizk_iters']), int(m['iter']), int(m['subiter']), int.from_bytes(base64.b64decode(m['challenge_response']), "big"))
             for m in nizk_line.finditer(contract, re.MULTILINE)]

# validate proof responses

def challenge(nizk_iters, iter):
    digest_length = 128 + 16 # 1024 bit + some extra to combat modulo bias
    entropy = hashlib.shake_256(f"{nizk_iters}:{iter}:{modulus}".encode("utf-8")).digest(digest_length)
    return int(f"0x{entropy.hex()}", 16) % modulus

assert len(responses) >= 16, "Zero knowledge proof too short!"
assert all([nizk_iters*2 == len(responses) for nizk_iters, _, _, _ in responses]), "Proof responses disagree on total count."
assert all([(iter, subiter) == divmod(idx, 2) for idx, (_, iter, subiter, _) in enumerate(responses)]), "Iters should increase sequentially."

for i in range(0, len(responses), 2):
    nizk_iters, iter, _, lo512 = responses[i]
    _, _, _, hi512 = responses[i+1]
    challenge_response = hi512 * 2**512 + lo512
    assert pow(challenge_response, 0x10001, modulus) == challenge(nizk_iters, iter), "Zero knowledge proof not valid!"

print(f"Zero knowledge proof is valid for modulus=0x{modulus:0128x}!")
