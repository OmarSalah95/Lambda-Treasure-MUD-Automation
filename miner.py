from api import url, key
import hashlib
import requests
import sys
from uuid import uuid4
from timeit import default_timer as timer
import random


def mine():
    """
    Simple Proof of Work Algorithm
    Stringify the block and look for a proof.
    Loop through possibilities, checking each one against `valid_proof`
    in an effort to find a number that is a valid proof
    :return: A valid proof for the provided block
    """
    data = requests.get(f"{url}/api/bc/last_proof/",
                        headers={'Authorization': f"Token {key}"})
    last_proof = data['proof']
    difficulty = data["difficulty"]
    
    
    previous_hash=hashlib.sha256(f'{last_proof}'.encode()).hexdigest()
    
    start = timer()
    
    print("Searching for next proof")
    proof = 0
    #  TODO: Your code here
    while not valid_proof(previous_hash, proof, difficulty):
        proof+=3126
    
    print("Proof found: " + str(proof) + " in " + str(timer() - start))
    
    json  = {"proof":proof}
    req = requests.post(f"{url}/api/bc/mine/ ",
                        headers={'Authorization': f"Token {key}", "Content-Type": "application/json"}, json=json)
    print("Proof Submitted")


def valid_proof(last_hash, proof, difficulty):
    """
    Validates the Proof:  Does hash(block_string, proof) contain 6
    leading zeroes?  Return true if the proof is valid
    :param block_string: <string> The stringified block to use to
    check in combination with `proof`
    :param proof: <int?> The value that when combined with the
    stringified previous block results in a hash that has the
    correct number of leading zeroes.
    :return: True if the resulting hash is a valid proof, False otherwise
    """
    guess = f'{last_hash}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:difficulty] == "0" * difficulty
