import sys
sys.path.append("../")
from globals import *

publicKey = BT_TREASURY
print(publicKey)

# - input public key
# - assume prior calendar year
# - figure out le tax
#   - sale proceeds 
#     - from purchase on Stellar
#     - from pre-existing cost basis
#       - incl. broker ACATS
#   - interest
#     - pay all dividends via USDC for recordkeeping?
# - pull pii record
# - sumbmit DIV to FIRE
# - export/email(?) 8949/DIV(?)