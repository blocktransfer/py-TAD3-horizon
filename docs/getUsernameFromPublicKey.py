import sys
sys.path.append("../")
from globals import *

def getUsernameFromPublicKey(PK):
  hash = SHA3(PK)
  encoded = base64.b64encode(hash)
  decoded = base64_hash.decode("utf-8").replace("/", "").replace("+", "").replace("=", "")
  return decoded[:16]

account_number = BT_TREASURY
username = getUsernameFromPublicKey(account_number)
print(f"Account Number: {account_number}, Username: {username}")
