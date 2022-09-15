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
  print(requestAddr)
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  b=9
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      IDs = trades["id"].split("-")[0]
      settlementTime = trades["ledger_close_time"]
      baseAddr = trades["base_account": "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY",
      trades["base_amount": "129.9633530",
      trades["base_asset_type": "credit_alphanum4",
      trades["base_asset_code": "USDC",
      trades["base_asset_issuer": "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN",
      trades["counter_offer_id": "997080830",
      trades["counter_account": "GBEZLZV7VUKAPQ5LME2SIGG5ER5RH5P22SRF5OP3HQCY6H6V6GCHISIN",
      trades["counter_amount": "129.9698449",
      trades["counter_asset_type": "credit_alphanum12",
      trades["counter_asset_code": "yUSDC",
      trades["counter_asset_issuer": "GDGTVWSM4MGS4T7Z6W4RPWOCHE2I6RDFCIFZGS3DOA63LWQTRNZNTTFF",
      : false,
      if():
        i am counter
      else:
        i am base
      
      
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
      
      
      
      
      bis = trades["trade_type"]
      if(bis != "orderbook"):
        pprint(trades)
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