import sys
sys.path.append("../")
from globals import *

publicKey = "GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG" #BT_TREASURY # testing

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years

# - input public key


# - assume prior calendar year
def mapOfferIDsToProceeds():
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/trades?limit={MAX_SEARCH}"
  #print(requestAddr)
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  a = b = ""
  while(blockchainRecords != []):
    #print(requestAddr)
    for trades in blockchainRecords:
      
      
      opID = trades["id"].split("-")[0]

      settlementTime = trades["ledger_close_time"]

      baseOfferID = trades["base_offer_id"]
      baseAddr = trades["base_account"]
      baseAmount = trades["base_amount"]
      try:
        baseAsset = Asset(trades["base_asset_code"], trades["base_asset_issuer"])
      except KeyError:
        baseAsset = Asset.native()
      
      counterOfferID = trades["counter_offer_id"]
      counterAddr = trades["counter_account"]
      counterAmount = trades["counter_amount"]
      
      try:
        counterAsset = Asset(trades["counter_asset_code"], trades["counter_asset_issuer"])
      except KeyError:
        counterAsset = Asset.native()
      
      investorOfferID = baseOfferID if baseAddr == publicKey else counterOfferID
      if(len(investorOfferID) > 12):
        a = trades
      else:
        b = trades
      

#      if():
#        i am counter
#      else:
#        i am base
      
      
      # extract asset
      # part of averaged single sale? -> begin averaging
        # sum all bought / sum all given etc
      # extract value at txn for own benefit
      
      # a way to work cost basis into this ?
      
      
      
      
      # BASICALLY:
      # Can create account record for uncovered positions or pre-existing basis totally averaged out mst likely
      # When they go to sell, they pick the lot
      # Lots classified by OFFER_ID and averages as needed when providing liquidity
      # When selling (from account omnibus), Use MEMO "Disposing #{OFFER_ID}"
      
      
      
      
      #bis = trades["trade_type"]
      #if(bis != "orderbook"):
      #  pprint(trades)
      #else:
      
      
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
  
    #- cycle through txns using taxYearStart to 
  
  pprint(b)
  
  taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
  return 0

def mapOfferIDsToMemos():
  return 1

mapOfferIDsToProceeds()
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