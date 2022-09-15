import sys
sys.path.append("../")
from globals import *

publicKey = BT_TREASURY # testing

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years

# - input public key


# - assume prior calendar year
def getAllTxnsFromLastYear():
  # - fetch account
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  a = 0
  b = 0
  while(blockchainRecords != []):
    print(requestAddr)
    for trades in blockchainRecords:
      bis = trades["base_is_seller"]
      if(bis):
        a += 1
      else:
        b += 1
      #for balances in accounts["balances"]:
      #  try:
      #    if balances["asset_code"] == queryAsset and balances["asset_issuer"] == BT_ISSUER:
      #      queryBalance = Decimal(balances["balance"])
      #  except Exception:
      #    continue
      #StellarBlockchainBalances[accountAddr] = queryBalance
      
#      for payments in accountPaymentRecords:
#            try:
#              if(payments["asset_type"] == "native" and payments["to"] == votingAddr and pandas.to_datetime(payments["created_at"]) < VOTE_CUTOFF_TIME_UTC):
#                transactionEnvelopeAddr = payments["_links"]["transaction"]["href"]
#                vote = requests.get(transactionEnvelopeAddr).json()["memo"]
#                addrsMappedToMemos[payments["from"]] = vote
#            except KeyError:
#              continue
      
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  
  
  print(a)
  print(b)
  #- cycle through txns using taxYearStart to 
  
  
  
  taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
  return 0


getAllTxnsFromLastYear()
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