import sys
sys.path.append("../")
from globals import *
from taxTestingData import *
import functools

# offerIDsMappedToChiefMemosForAccount = {} #tmp

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
washSaleAdjStart = taxYearStart - pandas.DateOffset(days = WASH_SALE_DAY_RANGE)
washSaleAdjCutoff = taxYearEnd + pandas.DateOffset(days = WASH_SALE_DAY_RANGE)

def bulkOutput():
  MICR_lines = ["access_me.csv"]
  for addresses in MICR_lines[0]:
    form8949forAccount(addresses)

def form8949forAccount(address):
  taxableSales = washSaleReferenceList = []
  offerIDsMappedToChiefMemosForAccount = getOfferIDsMappedToChiefMemosForAccount(address) # TODO: Impliment some kind of caching here (associated with MICR?)
  for offerIDs, memos in offerIDsMappedToChiefMemosForAccount.items():
    trade = getTradeData(offerIDs, address)
    if(trade[1] == "sell"):
      matchOfferID = offerIDsMappedToChiefMemosForAccount[offerIDs]
      print(matchOfferID)
      print(memos)
      origin = getTradeData(memos, address)
      combined = combineTradeData(trade[2], origin)
      pprint(combined)
      if(combined[0] == "covered"):
        combined += getCoveredPNLfromCombinedTrade(combined)
      else:
        combined += getUncoveredPNLfromCombinedTrade(combined, address)
      taxableSales.append(combined)
    else:
      washSaleReferenceList.append(trade)
  adjustedTrades = adjustAllTradesForWashSales(taxableSales, address, offerIDsMappedToChiefMemosForAccount)
  # mergedTrades = mergeForVARIOUS(adjustedTrades) ? or just do by orderID?
  finalTrades = filterTradesToTaxablePeriod(mergedTrades)
  finalFormData = placeFieldsplaceFields(adjustedTrades)
  #export to 8949 PDF(s)

def getOfferIDsMappedToChiefMemosForAccount(address):
  offerIDsMappedToChiefMemosForAccount = {}
  requestAddr = f"https://{HORIZON_INST}/accounts/{address}/transactions?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for txns in blockchainRecords:
      if(txns["source_account"] == address):
        resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
        for ops in resultXDR.result.results:
          ops = ops.tr
          if(ops.manage_buy_offer_result or ops.manage_sell_offer_result):
            offerIDarr = []
            appendOfferIDfromTxnOpToBaseArr(ops, offerIDarr, address, txns["result_xdr"])
            for offerIDs in offerIDarr:
              if(offerIDs and offerIDs not in offerIDsMappedToChiefMemosForAccount.keys()):
                try:
                  memo = txns["memo"]
                except KeyError:
                  memo = ""
                offerIDsMappedToChiefMemosForAccount[offerIDs] = memo
    blockchainRecords = getNextCursorRecords(data)
  return offerIDsMappedToChiefMemosForAccount

def rgetattr(obj, attr):
  def subgetattr(obj, attr):
      return getattr(obj, attr)
  return functools.reduce(subgetattr, [obj] + attr.split('.'))

def appendOfferIDfromTxnOpToBaseArr(op, offerIDarr, address, resultXDR):
  makerIDattr = "success.offer.offer.offer_id.int64"
  
  try:
    offerID = rgetattr(op.manage_sell_offer_result, makerIDattr)
  except AttributeError:
    try:
      offerID = rgetattr(op.manage_buy_offer_result, makerIDattr)
    except AttributeError:
      takerIDattr = "offer.offer.offer_id.int64"
      try:
        taker = op.manage_sell_offer_result.success
        offersClaimed = taker.offers_claimed
        offerID = addManyOffers(offersClaimed, offerIDarr, address) if len(offersClaimed) else getOfferIDfromContraID(rgetattr(taker, takerIDattr), address)
        pprint(op)
      except AttributeError:
        try:
        
          taker = op.manage_sell_offer_result.success # # #
          offersClaimed = taker.offers_claimed
          try:
            pprint(resultXDR)
            offerID = getOfferIDfromContraID(rgetattr(taker, takerIDattr), address)
          except AttributeError:
            try:
              offerID = addManyOffers(taker.offers_claimed, offerIDarr, address)
            except UnboundLocalError:
              print("LL")
              offerID = 0
          
        except AttributeError:
          sys.exit("never get here")
          effectIDattr = "success.offer.effect"
          deleteEffect = 2
          try:
            if(rgetattr(op.manage_sell_offer_result, effectIDattr) == deleteEffect):
              offerID = 0
          except AttributeError:
            try:
              if(rgetattr(op.manage_buy_offer_result, effectIDattr) == deleteEffect):
                offerID = 0
            except AttributeError:
              sys.exit(f"Failed to resolve offerID in\n{op}")
  return offerIDarr.append(offerID)

def addManyOffers(offersClaimed, offerIDarr, address):
  lastTrade = offersClaimed[-1:]
  IDattr = "offer_id.int64"
  pprint(offersClaimed)
  for trades in offersClaimed:
    try:
      offerID = getOfferIDfromContraID(rgetattr(trades.order_book, IDattr), address)
    except AttributeError:
      try:
        offerID = getOfferIDfromContraID(rgetattr(trades.liquidity_pool, IDattr), address)
      except AttributeError:
        try:
          offerID = getOfferIDfromContraID(rgetattr(trades.v0, IDattr), address)
        except AttributeError:
          sys.exit(f"Atomic swap contra discovery failed:\n{offersClaimed}")
    if(trade != lastTrade):
      offerIDarr.append(offerID)
    print(offerID)
  return offerID
  

def getOfferIDfromContraID(offerID, address):
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      try:
        if(trades["counter_account"] == address):
          return int(trades["counter_offer_id"])
        elif(trades["base_account"] == address):
          return int(trades["base_offer_id"])
      except KeyError:
        sys.exit(f"Error generating syntheic ID - check paging token\n{trades}")
    blockchainRecords = getNextCursorRecords(data)
  sys.exit(f"Could not find offerID from Omnibus Contra #{offerID}")

def getTradeData(offerID, address):
  try:
    int(offerID)
  except ValueError: 
    return 0
  tradeData = {}
  type = ""
  value = shares = Decimal("0")
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
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
          type = "buy"
        if(counterAssetFiat):
          value += Decimal(trades["counter_amount"])
          shares += Decimal(trades["base_amount"])
          if type: continue
          tradeData["asset"] = baseAsset
          type = "sell"
      elif(trades["counter_account"] == address):
        tradeData["asset"] = baseAsset
        if(counterAssetFiat):
          value += Decimal(trades["counter_amount"])
          shares += Decimal(trades["base_amount"])
          if type: continue
          tradeData["asset"] = baseAsset
          type = "buy"
        if(baseAssetFiat):
          value += Decimal(trades["base_amount"])
          shares += Decimal(trades["counter_amount"])
          if type: continue
          tradeData["asset"] = counterAsset
          type = "sell"
    tradeData["finalExecutionDate"] = pandas.to_datetime(trades["ledger_close_time"])
    blockchainRecords = getNextCursorRecords(data)
  tradeData["shares"] = shares
  tradeData["value"] = value
  return (offerID, type, tradeData) if value else 0

def getAssetGivenType(trade, type): # type <- "base" | "counter"
  try:
    return Asset(trade[f"{type}_asset_code"], trade[f"{type}_asset_issuer"])
  except KeyError:
    return Asset.native()

def isFiat(queryAsset):
  return queryAsset == USD_ASSET or queryAsset == USDC_ASSET

def combineTradeData(tradeData, originTradeData):
  if(not originTradeData):
    return(
      (
        "uncovered",
        tradeData["asset"],
        0, # given full  functionality,
        0, # combine into originTradeData["..."] if originTradeData else 0
        0,
        tradeData["shares"],
        tradeData["value"],
        tradeData["finalExecutionDate"]
      )
    )
  assert(tradeData["asset"] == originTradeData["asset"]) # todo, see above
  assert(originTradeData["finalExecutionDate"] < tradeData["finalExecutionDate"])
  return(
    (
      "covered",
      tradeData["asset"],
      originTradeData["finalExecutionDate"],
      originTradeData["shares"],
      originTradeData["value"],
      tradeData["shares"],
      tradeData["value"],
      tradeData["finalExecutionDate"],
    )
  )

def getCoveredPNLfromCombinedTrade(data):
  sharesBought = adjustSharesBoughtForStockSplits(data[3], data[2], data[1].code)
  purchaseBasis = data[4]
  sharesSold = data[5]
  saleProceeds = data[6]
  if(sharesBought == sharesSold):
    return(purchaseBasis, saleProceeds - purchaseBasis)
  elif(sharesBought > sharesSold):
    purchasePrice = sharesBought / purchaseBasis
    purchaseBasisAdj = sharesSold * purchasePrice
    return(purchaseBasisAdj, saleProceeds - purchaseBasisAdj)
  else:
    sys.exit("todo: test on live data")

def getUncoveredPNLfromCombinedTrade(data, addr):
  historicPositions = []
  # historicPositions = callToCloud()
  historicPositionData = "Address|Asset Code|Uncovered Share Aquisition Date|Data Migration Date|Uncovered Share Amount|Uncovered Share Basis\nGDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7|yUSDC|2020-9-15|2021-1-1|15000|256654\nGARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG|XLM|2018-9-15|2021-1-1|15000|3200"
  for lines in historicPositionData.split("\n")[1:]:
    for address, assetCode, purchaseDate, shares, basis in lines.split("|"):
      if(address == addr):
        historicPositions.append(
          (
            assetCode,
            pandas.to_datetime(f"{purchaseDate}T20:00:00Z"),
            Decimal(shares),
            Decimal(basis)
          )
        )
  # todo: impliment this with a backend database
  


  
        
        
        
# "uncovered",
# tradeData["asset"],
# 0,                                originTradeData["finalExecutionDate"],
# 0,                                originTradeData["shares"],
# 0,                                originTradeData["value"],
# tradeData["shares"],
# tradeData["value"],
# tradeData["finalExecutionDate"]
  comparableAssets = []
  for oldBuys in historicPositions:
    if(oldBuys[0] == data[1].code):
      comparableAssets.append(oldBuys)
  
  
  
  #what if instead of doing this, we just code it as independent txs with "offer codes" when sending shares initially
  fetchPreExistingPositions(address, data[1].code)
  
  sharesBought = adjustSharesBoughtForStockSplits(a, b, data[1].code)
  purchaseBasis = Decimal(getUncoveredBasis("Set up a basic google sheet")) if 0 else data[4]
  sharesSold = data[5]
  saleProceeds = data[6]
  pprint(data)
  if(sharesBought == sharesSold):
    return(purchaseBasis, saleProceeds - purchaseBasis)
  elif(sharesBought > sharesSold):
    purchasePrice = sharesBought / purchaseBasis
    purchaseBasisAdj = sharesSold * purchasePrice
  return (purchaseBasisAdj, saleProceeds - purchaseBasis)

def fetchInvestorPreExistingPositionsForAsset(address, queryAsset):
  preExistingPositions = []
  requestAddr = f"https://{HORIZON_INST}/accounts/{address}/payments?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for payments in blockchainRecords:
      try:
        properAsset = Asset(payments["asset_code"], payments["asset_issuer"]) == Asset(queryAsset, BT_ISSUER)
      except KeyError:
        continue
      if(properAsset and payments["from"] == BT_DISTRIBUTOR):
        txnAddr = payments["_links"]["transaction"]["href"]
        txnData = requests.get(txnAddr).json()
        try:
          priorBase = txnData["memo"] # Expect YEAR-MONTH-DAY@PRICE | uncovered
        except KeyError:
          sys.exit(f"Unlabelled distribution:\n{payments}") # TODO: DWAC transfers don't include the basis - brokers send it separately within a month, so we need some kind of other record for this 
        preExistingPositions.append((payments["amount"], priorBase))
    blockchainRecords = getNextCursorRecords(data)
  return preExistingPositions

def getUncoveredBasis(data):
  # you can't get the basis for uncovered shares ?
  return 1

def adjustSharesBoughtForStockSplits(numShares, purchaseTimestamp, queryAsset):
  splitsDict = getSplitsDict(queryAsset)
  for splitTimestamps, splitRatios in splitsDict.items():
    if(purchaseTimestamp < splitTimestamps):
      numShares = numShares * splitRatios
  return numShares

def getSplitsDict(queryAsset):
  splitsDict = {}
  try:
    requestAddr = "https://blocktransfer.io/.well-known/stellar.toml"
    data = toml.loads(requests.get(requestAddr).content.decode())
    for currencies in data["CURRENCIES"]:
      if(currencies["toml"][32:-5] == queryAsset): # format asset as toml link
        data = toml.loads(requests.get(currencies["toml"]).content.decode())
        splitData = data["CURRENCIES"][0]["splits"].split("|")
        for splits in splitData:
          date = pandas.to_datetime(f"{splits.split('effective ')[1]}T00:00:00Z")
          flexData = splits.split(" ")
          num = Decimal(flexData[0])
          denom = Decimal(flexData[2])
          splitsDict[date] = num / denom
        return splitsDict
  except Exception:
    sys.exit(f"Failed to lookup split info for {queryAsset}")

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
# 0   "covered",
# 1   tradeData["asset"],
# 2   originTradeData["finalExecutionDate"],
# 3   originTradeData["shares"],
# 4   originTradeData["value"],
# 5   tradeData["shares"],
# 6   tradeData["value"],
# 7   tradeData["finalExecutionDate"],
# 8   purchaseBasisAdj
# 9  PNL
  
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
  return washSaleAdjStart <= sale[2]["finalExecutionDate"] <= washSaleAdjCutoff

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

# print(adjustSharesBoughtForStockSplits(Decimal("100"), date, "DEMO"))
form8949forAccount("GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG")
fetchPreExistingPositionsForAsset("GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML", "DEMO")