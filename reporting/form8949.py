import sys
sys.path.append("../")
from globals import *
import taxTestingData

# TODO: Impliment some kind of caching for offerIDsMappedToChiefMemosForAccount associated with investor data

publicKey = BT_TREASURY #"GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG" # testing
allOfferIDsMappedToChiefMemosForAccount = {}

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week

def form8949forAccount():
  # getAllOfferIDsMappedToChiefMemosForAccount(publicKey)
  (buyOfferIDsMappedToCostBasis, sellOfferIDsMappedToProceeds) = getTradesWithBasisOrProceedsFromOfferID()
  calculateYearlyPNL(publicKey)

# get lot sale instr. from memo using offerID txns
# -- full takes = easy memo id from op
# -- makes = shows other guy SO we need the original sell offer txn obj

# FIELD NEEDED:
# Description of property
# Date acquired
# Date sold
# Proceeds
# Basis
# Adjustment/wash sale
# PNL

# - assume prior calendar year
def calculateTaxYearPNL():
  # figure out which offer IDs where sales this tax year 
  getTradesWithBasisOrProceedsFromOfferID
  
  
  
  
  
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
      
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  
    #- cycle through txns using taxYearStart to 
  
  pprint(b)
  
  return 0

# - figure out le tax
#   - sale proceeds 
#     - from purchase on Stellar
#     - from pre-existing cost basis
#       - incl. broker ACATS
# - pull pii record which has association for uncovered securities or pre-existing cost basis
# - sumbmit DIV to FIRE
# - export/email(?) 8949

# different doc:
#   - interest
#     - pay all dividends via USDC for recordkeeping?
# - export DIV


def getAllOfferIDsMappedToChiefMemosForAccount(publicKey):
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/transactions?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for txns in blockchainRecords:
      if(txns["source_account"] != publicKey):
        continue
      resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
      for ops in resultXDR.result.results:
        offerIDarr = []
        getOfferIDfromTxnOp(ops, offerIDarr)
        for offerIDs in offerIDarr:
          if(offerIDs and offerIDs not in allOfferIDsMappedToChiefMemosForAccount.keys()):
            try:
              memo = txns["memo"]
            except KeyError:
              memo = ""
            allOfferIDsMappedToChiefMemosForAccount[offerIDs] = memo
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("\u0026", "&")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  return 1

def getOfferIDfromTxnOp(op, offerIDarr):
  try:
    offerID = op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64
  except AttributeError:
    try:
      offerID = op.tr.manage_buy_offer_result.success.offer.offer.offer_id.int64
    except AttributeError:
      try:
        atomicSwaps = op.tr.manage_sell_offer_result.success.offers_claimed
        if(len(atomicSwaps)):
          offerID = appendAtomicSwapOfferIDsToArr(atomicSwaps, offerIDarr)
        else:
          offerID = getOfferIDfromOmnibusContraOfferID(op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64)
      except AttributeError:
        try:
          atomicSwaps = op.tr.manage_buy_offer_result.success.offers_claimed
          if(len(atomicSwaps)):
            offerID = appendAtomicSwapOfferIDsToArr(atomicSwaps, offerIDarr)
          else:
            offerID = getOfferIDfromOmnibusContraOfferID(op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64)
        except:
          return 0
  offerIDarr.append(offerID)
  return 1

def appendAtomicSwapOfferIDsToArr(atomicSwaps, offerIDarr):
  for trades in atomicSwaps:
    try:
      offerID = getOfferIDfromOmnibusContraOfferID(trades.order_book.offer_id.int64)
    except AttributeError:
      try:
        offerID = getOfferIDfromOmnibusContraOfferID(trades.liquidity_pool.offer_id.int64)
      except AttributeError:
        try:
          offerID = getOfferIDfromOmnibusContraOfferID(trades.v0.offer_id.int64)
        except:
          sys.exit("Atomic swap contra discovery failed")
    offerIDarr.append(offerID)
  return offerID

def getOfferIDfromOmnibusContraOfferID(offerID):
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      try:
        if(trades["counter_account"] == publicKey):
          offerID = trades["counter_offer_id"]
        elif(trades["base_account"] == publicKey):
          offerID = trades["base_offer_id"]
      except KeyError:
        sys.exit(f"Error generating syntheic ID - check paging token")
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  return int(offerID)

def getBasisOrProceedsFromTrade():
  return 1

def getTradeProceedsFromOfferID(): # call if in tax year
  return 1

def getTradeQuantityAndBasisFromOfferID():
  return 1

def getTrades_Date_FromOfferID():
  totalFiatCost = totalFiatProceeds = totalSharesPurchased = totalSharesSold = Decimal("0")
  requestAddr = f"https://{HORIZON_INST}/offers/{offerIDs}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      try:
        baseAsset = Asset(trades["base_asset_code"], trades["base_asset_issuer"])
      except KeyError:
        baseAsset = Asset.native()
      baseAssetFiat = baseAsset == USD_ASSET or baseAsset == USDC_ASSET
      try:
        counterAsset = Asset(trades["counter_asset_code"], trades["counter_asset_issuer"])
      except KeyError:
        counterAsset = Asset.native()
      counterAssetFiat = counterAsset == USD_ASSET or counterAsset == USDC_ASSET
      # Expect one asset to be fiat
      if(trades["base_account"] == publicKey):
        if(baseAssetFiat):
          totalFiatCost += Decimal(trades["base_amount"])
          totalSharesPurchased += Decimal(trades["counter_amount"])
        elif(counterAssetFiat):
          totalFiatProceeds += Decimal(trades["counter_amount"])
          totalSharesSold += Decimal(trades["base_amount"])
      elif(trades["counter_account"] == publicKey):
        if(counterAssetFiat):
          totalFiatCost += Decimal(trades["counter_amount"])
          totalSharesPurchased += Decimal(trades["base_amount"])
        elif(baseAssetFiat):
          totalFiatProceeds += Decimal(trades["base_amount"])
          totalSharesSold += Decimal(trades["counter_amount"])
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  if(totalSharesPurchased and totalSharesSold):
    sys.exit("Critical math error")
  return (totalFiatCost, totalFiatProceeds)




# step 1: get everything working
# step 2: deal with wash sales :)
# future features: support liquidity pool D/W
#                     (as interest income or cap gains? many aquisitions/dispositions?)
#                  path payments (incl. to self)

getAllOfferIDsMappedToChiefMemosForAccount(publicKey)
print(allOfferIDsMappedToChiefMemosForAccount)