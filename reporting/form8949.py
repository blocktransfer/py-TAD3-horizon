import sys
sys.path.append("../")
from globals import *

publicKey = BT_TREASURY # testing

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years

# - input public key


# - assume prior calendar year
def getAllTxnsFromLastYear():
  - fetch account
  - cycle through txns using taxYearStart to 
  taxYearEnd = taxYearStart + # modify here for 52-53-week tax year
  return 0



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