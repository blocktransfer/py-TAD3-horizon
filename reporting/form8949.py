import sys
sys.path.append("../")
from globals import *

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
# washSaleAdjStart = taxYearStart - pandas.DateOffset(days = WASH_SALE_DAY_RANGE)
# washSaleAdjCutoff = taxYearEnd + pandas.DateOffset(days = WASH_SALE_DAY_RANGE)

def bulkOutput():
  MICR = open(MICR_TXT)
  for lines in MICR:
    print(lines)
    account = lines.split("|")
    form8949forAccount(account[0])
  MICR.close()

## Testing needed at scale
# import threading
# threads = []
# for addresses, i in enumerate(lines.split("|")[0]):
#   form8949forAccount(addresses)
#   threads.append(
#       threading.Thread(
#         target = form8949forAccount,
#         args = (addresses,)
#       )
#     )
#   threads[i].start().join()
##

def form8949forAccount(address):
  allTrades = []
  offerIDsMappedToChiefMemos = getOfferIDsMappedToChiefMemosFromCache()
  for offerIDs, memos in offerIDsMappedToChiefMemos.items():
    requestAddr = f"{HORIZON_INST}/offers/{offerIDs}/trades"
    # memo format {refOfferID}|cachedAddr
    memo = memos.split("|")
    instructions = memo[0]
    address = memo[1]
    offerTradeData = getTradeData(offerIDs, address)
    if(offerTradeData["type"] == "out"): 
      if(taxYearStart <= offerTradeData["fillDate"] < taxYearEnd):
        openingOfferID = offerIDsMappedToChiefMemos[offerIDs]
        originTradeData = getTradeData(instructions, address)
        combinedTradeData = combineTradeData(offerTradeData, originTradeData)
        reportingTradeData = getTradePNL(combinedTradeData, instructions, address)
        allTrades.append(reportingTradeData)
  
  finalFormData = placeFieldsplaceFields(adjustedTrades)
  exportForm8949(finalFormData)

# a = [{'PNL': Decimal('105.2399095'),
#  'asset': Asset("DEMO", BT_ISSUER),
#  'badOriginData': True,
#  'exitOfferID': 862213103,
#  'exitTradeDate': pandas.to_datetime("2021-12-03 14:12:53"),
#  'exitTradeShares': Decimal('297.6174592'),
#  'exitTradeValue': Decimal('106.2399095'),
#  'originOfferID': 0,
#  'originTradeDate': 0,
#  'originTradeShares': 0,
#  'originTradeValue': 0}]
# pprint(a.items())
# print("\n")
# pprint(Asset("DEMO", BT_ISSUER) in a.values())
# print("\n")
# for v in a.values():
#   print(v)
# sys.exit()

# b = len("1234567890123456")
# if(b < 16):
#   offerID
# elif(b < 19)
#   synthetic
# else: 
#   PT

def generateAnnual8949(allTrades):
  taxableTrades = []
  usedDatesMappedToAssets = {}
  for trades in allTrades:
    fillDate = trades["exitTradeDate"]
    if(taxYearStart <= fillDate < taxYearEnd):
      dateInForm = fillDate.date() in taxableTradeDatesMappedToTradeAsset.keys()
      sameAssetAlreadyOnThisDay = usedDatesMappedToAssets[fillDate.date()] == trades["asset"]
      if():
        return 1
      for existing in taxableTrades:
        if(trades["exitTradeDate"].date() == existing["exitTradeDate"].date()):
          trades = merge
      
      
      if(trades["exitTradeDate"].date() in taxableTrades):
        mergeTogether = 1
      else:
        taxableTrades.append(trades)
    
    # mergeForVARIOUS

def getTradeData(offerID, address):
  tradeData = {"type": 0}
  type = ""
  value = shares = Decimal("0")
  try:
    requestAddr = f"{HORIZON_INST}/offers/{int(offerID)}/trades?{MAX_SEARCH}"
  except ValueError:
    return tradeData
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for trades in ledger["_embedded"]["records"]:
      baseAsset = getAssetGivenType(trades, "base")
      counterAsset = getAssetGivenType(trades, "counter")
      baseAssetFiat = isFiat(baseAsset)
      counterAssetFiat = isFiat(counterAsset)
      # Expect exactly one fiat asset
      if(trades["base_account"] == address):
        if(baseAssetFiat):
          value += Decimal(trades["base_amount"])
          shares += Decimal(trades["counter_amount"])
          if type: continue
          tradeData["asset"] = counterAsset
          type = "in"
        if(counterAssetFiat):
          value += Decimal(trades["counter_amount"])
          shares += Decimal(trades["base_amount"])
          if type: continue
          tradeData["asset"] = baseAsset
          type = "out"
      elif(trades["counter_account"] == address):
        tradeData["asset"] = baseAsset
        if(counterAssetFiat):
          value += Decimal(trades["counter_amount"])
          shares += Decimal(trades["base_amount"])
          if type: continue
          tradeData["asset"] = baseAsset
          type = "in"
        if(baseAssetFiat):
          value += Decimal(trades["base_amount"])
          shares += Decimal(trades["counter_amount"])
          if type: continue
          tradeData["asset"] = counterAsset
          type = "out"
    tradeData["fillDate"] = pandas.to_datetime(trades["ledger_close_time"])
    ledger = getNextLedgerData(ledger)
  tradeData["offerID"] = offerID
  tradeData["shares"] = shares
  tradeData["value"] = value
  tradeData["type"] = type
  return tradeData

def getAssetGivenType(trade, type):
  try:
    return Asset(trade[f"{type}_asset_code"], trade[f"{type}_asset_issuer"])
  except KeyError:
    return Asset.native()

# todo - check on live data for:
# assert(tradeData["asset"] == originTradeData["asset"])
# assert(originTradeData["fillDate"] < tradeData["fillDate"])
def combineTradeData(tradeData, originTradeData):
  combined = {}
  combined["asset"] = tradeData["asset"]
  combined["originOfferID"] = originTradeData["offerID"] if originTradeData["type"] else 0
  combined["originTradeDate"] = originTradeData["fillDate"] if originTradeData["type"] else 0
  combined["originTradeShares"] = adjustNumSharesForStockSplits(
    originTradeData["shares"],
    originTradeData["fillDate"],
    originTradeData["asset"].code
  ) if originTradeData["type"] else 0
  combined["originTradeValue"] = originTradeData["value"] if originTradeData["type"] else 0
  combined["exitOfferID"] = tradeData["offerID"]
  combined["exitTradeDate"] = tradeData["fillDate"]
  combined["exitTradeShares"] = tradeData["shares"]
  combined["exitTradeValue"] = tradeData["value"]
  return combined

# paging_token_EX = "111720727958269953"
# data_EX = "DEMO:4000:17.22:2003-6-9"
# distributionPagingTokensMappedToHistoricData = {}
# accountData[paging_token_EX] = data_EX # testing

def getTradePNL(fill, instructions, address):
  if(not fill["originTradeValue"]):
    fill.update(getOriginDataFromPagingToken(instructions, address))
  if(fill["originTradeShares"] == fill["exitTradeShares"]):
    fill["PNL"] = fill["exitTradeValue"] - fill["originTradeValue"]
  elif(fill["originTradeShares"] > fill["exitTradeShares"]):
    entryPrice = fill["originTradeShares"] / fill["originTradeValue"]
    originBasisAdj = fill["exitTradeShares"] * entryPrice
    fill["PNL"] = fill["exitTradeValue"] - originBasisAdj
  else:
    fill["PNL"] = fill["exitTradeValue"]
  fill["PNL"] -= adjustForWashSale(fill)
  return fill

def getOriginDataFromPagingToken(opPagingToken, address):
  originDistributionData = {}
  requestAddr = f"{HORIZON_INST}/operations/{opPagingToken}"
  try:
    opData = requests.get(requestAddr).json()["created_at"]
  except KeyError:
    return {"badOriginData": True}
  transactionAddr = opData["_links"]["transaction"]["href"]
  try:
    memo = requests.get(transactionAddr).json()["memo"]
  except KeyError: # [price]||uncovered||DWAC:[coveredDate]||
    memo = "uncovered:" 
  memo = memo.split(":")
  match memo[0]:
    case "uncovered":
      legacyPrice = Decimal("0")
    case "DWAC":
      try:
        legacyPrice = Decimal(getAccountDataDict(address)[f"DWAC-{opPagingToken}"])
      except KeyError:
        sys.exit(f"{address} missing DWAC mapping for {opPagingToken}")
    case other:
      legacyPrice = Decimal(memo[0])
  originDistributionData["originTradeDate"] = memo[1]
  originDistributionData["originTradeShares"] = adjustNumSharesForStockSplits(
    opData["amount"],
    opData["created_at"],
    opData["asset_code"]
  )
  originDistributionData["originTradeValue"] = legacyPrice * opData["amount"]
  return originDistributionData

def adjustForWashSale(fill):
  # search data dict for origin offer id adj
  
  
  return 1

def getWashSaleOfferIDs(address):
  return 1

def getWashSaleAdjustments(address):
  return 1

def getAccountDataDict(address):
  requestAddr = f"{HORIZON_INST}/accounts/{address}"
  return requests.get(requestAddr).json()["data"]

# paging_token: basis
def basisFromAccountData(addr):
  data = getAccountDataDict(addr)
  historicPositionsCUSIPsMappedToBasisData = {}
  for key, value in data.items():
    if(isCUSIP(key)):
      historicPositionsCUSIPsMappedToBasisData[key] = value
  return historicPositionsCUSIPsMappedToBasisData

# [succeedingOfferID]: [lossDissallowedFromPriorTrade]
def getWashSalesFromAccountData(addr):
  data = getAccountDataDict(addr)
  succeedingOffersMappedToBasisAdjustments = {}
  for key, value in data.items():
    if(key in offerIDsMappedToChiefMemosForAccount.keys()):
      succeedingOffersMappedToBasisAdjustments[key] = value
  return succeedingOffersMappedToBasisAdjustments

def getUncoveredBasis(data):
  # you can't get the basis for uncovered shares ?
  return 1



def adjustAllTradesForWashSales(combinedData, address):
  adjustedTrades = washSaleWatchlist = []
  replacementOptions = []
  for combinedTrades in combinedData:
    if(combinedTrades[9] < 0):
      washSaleWatchlist.append(combinedTrades)
  for potentialWashes in washSaleWatchlist:
    # get all buys for stock
    
    for combinedTrades in combinedData:
      # combinedData is only for sales 
      #
      a=1
      #if(combinedTrades[1]
  
  if(washSaleAdjStart < saleTimestamp < taxYearStart):
    a = 1 
    
    matchOfferID = offerIDsMappedToChiefMemosForAccount[offerID]
    adjustForModifiedBasisFromTwoYearsPrior(purchaseOfferID, address, offerIDsMappedToChiefMemosForAccount)
    return ans
    
    
    return tradeData
    
  return adjustedTrades

def adjustForModifiedBasisFromTwoYearsPrior(purchaseOfferID, address, offerIDsMappedToChiefMemosForAccount):
  adjustedTrades = []
  return 1
  
  #origin = getBuyTradeData(matchOfferID, address)
  origin = 1
  combined = combineTradeData(sale[2], origin)
  if(combined[0] == "covered"):
    (basis, proceeds) = getCoveredBasisAndProceeds(combined)
    combined += (basis, proceeds, proceeds - basis)
  ss.append(combined) 

def filterTradesToTaxablePeriod(finalTrades):
  return washSaleAdjStart <= sale[2]["fillDate"] <= washSaleAdjCutoff

def placeFields(adjustedTrades):
  return 1
# FIELD NEEDED:
# Description of property via getCUSIP(asset.code)
# Date acquired
# Date sold
# Proceeds
# Basis
# Adjustment/wash sale
# PNL

# future features: support liquidity pool D/W
#                     (as interest income or cap gains? many aquisitions/dispositions?)
#                  support for sending path payments (incl. to self)

# testing: "GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG"
# print(getHistoricPositions("GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML"))
# print(getHistoricPositionsFromAccountData("GAJ4BSGJE6UQHZAZ5U5IUOABPDCYPKPS3RFS2NVNGFGFXGVQDLBQJW2P"))
# print(adjustSharesBoughtForStockSplits(Decimal("100"), date, "DEMO"))
form8949forAccount(BT_ISSUER)
#form8949forAccount("GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG")
#fetchInvestorPreExistingPositionsForAsset("GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML", "DEMO")






