from stellar_sdk import Keypair
from stellar_sdk import exceptions
import random, string, sys

def getLast3bytesToMakeValidStellarPublicKeyIfPossible(publicKey):
  base32Alphabet = string.ascii_uppercase + '234567'
  print(f"Testing {publicKey}")
  for char1 in base32Alphabet:
    for char2 in base32Alphabet:
      for char3 in base32Alphabet:
        try:
          answer = f"{publicKey}{char1}{char2}{char3}"
          keypair = Keypair.from_public_key(answer)
          return char1, char2, char3
        except exceptions.Ed25519PublicKeyInvalidError:
          continue
  return 0, 0, 0

def generateVanityPhraseInclPublicKey(phrase):
  if(len(phrase) >= 53):
    sys.exit("Try a shorter phrase")
  while True:
    keypair = Keypair.random()
    publicKey = keypair.public_key
    publicKey = publicKey[:-3]
    startIndex = random.randint(1, len(publicKey) - len(phrase))
    endIndex = startIndex + len(phrase)
    publicKey = f"{publicKey[:startIndex]}{phrase}{publicKey[endIndex:]}"
    char1, char2, char3 = getLast3bytesToMakeValidStellarPublicKeyIfPossible(publicKey)
    if char1:
      print(f"\n\tVALID:\n\t{publicKey}{char1}{char2}{char3}\n")
      return 1

generateVanityPhraseInclPublicKey("BLOCKTRANSFER777EMPLOYEECOMPENSATION777WITHOUTVOTING")