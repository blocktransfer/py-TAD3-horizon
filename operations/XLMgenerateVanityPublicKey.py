from stellar_sdk import Keypair, exceptions
import base64, binascii, random, string, sys

def getValidStellarPublicKeyIfExists(publicKeyNoChecksum):
  base32Alphabet = string.ascii_uppercase + '234567'
  print(f"Testing {publicKeyNoChecksum}")
  for char1 in base32Alphabet:
    for char2 in base32Alphabet:
      for char3 in base32Alphabet:
        try:
          trying = f"{publicKeyNoChecksum}{char1}{char2}{char3}"
          keypair = Keypair.from_public_key(trying)
          return trying
        except exceptions.Ed25519PublicKeyInvalidError:
          continue
  return 0

def generatePubKeyWithVanityPhrase():
  phrase = input("Enter the desired vanity phrase: ").upper()
  if len(phrase) >= 53:
    sys.exit("Try a shorter phrase")
  try:
    padding = "=" * (8 - len(phrase) % 8)
    base64.b32decode(phrase + padding)
  except (TypeError, binascii.Error):
    sys.exit("Try a base32 phrase")
  while True:
    publicKey = Keypair.random().public_key
    PKnoChecksum = publicKey[:-3]
    phraseInsertStartIndex = random.randint(1, len(PKnoChecksum) - len(phrase))
    phraseInsertEndIndex = phraseInsertStartIndex + len(phrase)
    PKnoChecksumWithPhrase = (
      PKnoChecksum[:phraseInsertStartIndex] +
      phrase +
      PKnoChecksum[phraseInsertEndIndex:]
    )
    PK = getValidStellarPublicKeyIfExists(PKnoChecksumWithPhrase)
    if PK:
      sys.exit(f"\n\tVALID:\n\t{PK}\n")

# Example usage:
generatePubKeyWithVanityPhrase()
