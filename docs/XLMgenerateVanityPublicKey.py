from stellar_sdk import Keypair
import random, string

def getLast3BytesToMakeValidStellarPublicKeyIfPossible(publicKey):
  base32Alphabet = string.ascii_uppercase + '234567'
  print(f"Testing {publicKey}")
  for char1 in base32Alphabet:
    for char2 in base32Alphabet:
      for char3 in base32Alphabet:
        try:
          answer = f"{publicKey}{char1}{char2}{char3}"
          keypair = Keypair.from_public_key(answer)
          return char1, char2, char3
        except:
          continue
  return 0, 0, 0

def generateVanityPhraseInclPublicKey(phrase):
  while True:
    keypair = Keypair.random()
    publicKey = keypair.public_key
    publicKey = publicKey[:-3]
    startIndex = random.randint(0, len(publicKey) - len(phrase))
    endIndex = startIndex + len(phrase)
    publicKey = f"{publicKey[:startIndex]}{phrase}{publicKey[endIndex:]}"
    char1, char2, char3 = getLast3BytesToMakeValidStellarPublicKeyIfPossible(publicKey)
    if char1:
      print(f"\n\tVALID:\n\t{publicKey}{char1}{char2}{char3}\n")
      return 1

generateVanityPhraseInclPublicKey("BLOCKTRANSFEROOOEMPLOYEECOMPENSATION")