import sys
sys.path.append("../")
from globals import *

def getAccountIDfromPublicKey(PK):
  PKhash = base64.b32encode(
    bytes.fromhex(
      SHA3(PK)
    )
  ).decode()
  PKhash = base64.b32encode(
    sha3_256(
      PK.encode()
    ).digest()
  ).decode()
  return PKhash[23:32]


BASE32_ALPHABET = string.ascii_uppercase + '234567'

def generate_random_base32_chars(length=8):
  return ''.join(random.choices(BASE32_ALPHABET, k=length)

def calculate_checksum(input_str):
  checksum_hash = sha3_256(input_str.encode()).hexdigest()
  print(f"checksum_hash: {checksum_hash}")
  checksum_integer = int(checksum_hash, 16)
  print(f"checksum_integer: {checksum_integer}")
  checksum_digit = checksum_integer % 32
  print(f"checksum_digit: {checksum_digit}")
  return checksum_digit

def generate_account_number():
  random_chars = generate_random_base32_chars()
  checksum_digit = calculate_checksum(random_chars)
  account_number = random_chars + BASE32_ALPHABET[checksum_digit]
  return account_number

# Generate a unique base32 9-digit account number
account_number = generate_account_number()
print(f"Unique Account Number: {account_number}")
sys.exit()



i = 1
while i < 11:
  i += 1
  PK = Keypair.random().public_key
  print(getAccountIDfromPublicKey(PK))
  continue
  base32Alphabet = string.ascii_uppercase + '234567'
  print( ''.join(random.choices(base32Alphabet, k=9)) )
  #fullCODE = base64.b32encode(sha3_256(PK.encode()).digest())[:-4].decode('ascii')
sys.exit()
print(BT_API_SERVER[8:])
print(fetchAccount(BT_TREASURY))
print(getAllPublicKeys())
for accounts in getAllPublicKeys():
  username = getAccountIDfromPublicKey(accounts)
  print(f"{accounts} -> {username}")
