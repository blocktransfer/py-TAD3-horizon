import sys
sys.path.append("../")
from globals import *

publicKey = "GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG" #BT_TREASURY # testing

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week




# get buy offerIDs

# get sell offerIDs

# get lot sale instr. from memo using offerID txns
# -- full takes = easy memo id from op
# -- makes = shows other guy SO we need the original sell offer txn obj



# use paging token as buy "trade number"
# - input public key
def mapBuyOfferIDsToCostBasis():
  return 1

# - assume prior calendar year
def mapSellOfferIDsToProceeds():
  offerIDsMappedToProceeds = {}
  
  
  
  
  
  
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/trades?limit={MAX_SEARCH}"
  #print(requestAddr)
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  lastOfferID = totalProceeds = 0
  while(blockchainRecords != []):
    #print(requestAddr)
    proceeds = 3000000
    cost = 10
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
      if(investorOfferID == lastOfferID):
        totalProceeds += proceeds
        totalCost += cost
      else:
        if(not totalProceeds):
          totalProceeds = proceeds
          totalCost = cost
        else:
          offerIDsMappedToProceeds[lastOfferID] = totalProceeds / totalCost
          totalProceeds = totalCost = 0
      
      
      
      if(len(investorOfferID) < 12):
        print(trades["_links"]["operation"])
        print(investorOfferID)
      
      instructions = getMemoFromMakerOfferID(publicKey, investorOfferID)
      
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
  
  return 0

def mapSellOfferIDsToMemos():
  return 1

#### mapSellOfferIDsToProceeds()



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



# todo: gain from path payments to self
# liquidity pools = interest income?




def getMemoFromMakerOfferID(publicKey, investorOfferID):
  offerAddr = f"https://{HORIZON_INST}/offers/investorOfferID"
  data = requests.get(requestAddr).json()
  offer = 
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/transactions?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  #print(requestAddr)
  a= "1063202185"
  # go through an find first instance of investorOfferID
  while(blockchainRecords != []):
    for txns in blockchainRecords:
    
      operationsAddr = txns["_links"]["operations"]["href"].replace("{?cursor,limit,order}", f"?limit={MAX_SEARCH}")
      data = requests.get(operationsAddr).json()
      opType = data["_embedded"]["records"][0]["type"]
      
      #pprint(opType)
      
      tradingOps = ["manage_sell_offer", "create_passive_sell_offer", "manage_buy_offer", "create_passive_buy_offer"]
      if(opType in tradingOps):
        offID = data["_embedded"]["records"][0]["offer_id"]
        #z=data["_embedded"]["records"][0]['created_at']
        #print(f"{z}:\t{offID}")
        
        
        
        
        
        
        
        
        
        if(not offID):
          data["_embedded"]["records"][0]["paging_token"]
        #if(offID=="0"):
        #  pprint(data)
        
      # manage buy offer
      # manage sell offer
      # those again but passive
    
    a=requestAddr
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  print(a)

getMemoFromMakerOfferID(publicKey, "48629595")














