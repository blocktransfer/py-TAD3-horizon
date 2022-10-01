import sys
sys.path.append("../")
from globals import *
import functools, threading #todo: threads -> global
from taxTestingData import *

USD_ASSET = Asset("TERN", "GDGQDVO6XPFSY4NMX75A7AOVYCF5JYGW2SHCJJNWCQWIDGOZB53DGP6C") # GARLIC testing
# offerIDsMappedToChiefMemosForAccount = {} #override external tax data
#print(range(1,18))
#tradeMemo = "4788099622563426305"
#match len(tradeMemo.split("-")[0]):
#  case <17:
#    return "offerID"
#  case => 17 and <= 18:
#    return "synthetic"
#  case 19:
#    return "paging_token"



lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
washSaleAdjStart = taxYearStart - pandas.DateOffset(days = WASH_SALE_DAY_RANGE)
washSaleAdjCutoff = taxYearEnd + pandas.DateOffset(days = WASH_SALE_DAY_RANGE)

def bulkOutput():
  MICRlines = open("access_me.txt").readlines().split("\n")
  threads = []
  for addresses, i in enumerate(MICRlines.split("|")[0]):
    form8949forAccount(addresses)
    threads.append(
        threading.Thread(
          target = form8949forAccount,
          args = (addresses,)
        )
      )
    threads[i].start().join()

def form8949forAccount(address):
  washSaleOfferIDs = getWashSaleOfferIDs(address)
  # TODO: Impliment dict caching w/ MICR: start at last known offerID timestamp
  offerIDsMappedToChiefMemosForAccount = getOfferIDsMappedToChiefMemosForAccount(address) 
  for offerIDs, memoOpeningInstr in offerIDsMappedToChiefMemosForAccount.items():
    offerTradeData = getTradeData(offerIDs, address)
    if(offerTradeData["type"] == "sell"): # sell = closing (todo: support short sales by adding "exit" flag)
      openingOfferID = offerIDsMappedToChiefMemosForAccount[offerIDs]
      openingTradeData = getTradeData(memoOpeningInstr, address)
      combinedTradeData = combineTradeData(offerTradeData, openingTradeData)
      reportingTradeData = getTradePNL(combined, address)
      
      taxableSales.append(combined)

  adjustedTrades = adjustAllTradesForWashSales(taxableSales, address, offerIDsMappedToChiefMemosForAccount)
  # mergedTrades = mergeForVARIOUS(adjustedTrades) ? or just do by orderID?
  finalTrades = filterTradesToTaxablePeriod(mergedTrades)
  finalFormData = placeFieldsplaceFields(adjustedTrades)
  #export to 8949 PDF(s)

def getOfferIDsMappedToChiefMemosForAccount(address):
  offerIDsMappedToChiefMemosForAccount = {}
  requestAddr = f"{HORIZON_INST}/accounts/{address}/transactions?{MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for txns in ledger["_embedded"]["records"]:
      if(txns["source_account"] == address):
        resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
        for ops in resultXDR.result.results:
          op = ops.tr
          if(op.manage_buy_offer_result or op.manage_sell_offer_result):
            offerIDarr = []
            appendOfferIDsToArr(op, offerIDarr, address)
            for offerIDs in offerIDarr:
              if(offerIDs and offerIDs not in offerIDsMappedToChiefMemosForAccount.keys()):
                try:
                  memo = txns["memo"]
                except KeyError:
                  memo = ""
                offerIDsMappedToChiefMemosForAccount[offerIDs] = memo
    ledger = getNextLedgerData(ledger)
  return offerIDsMappedToChiefMemosForAccount

def getAttr(obj, attr):
  def subGetAttr(obj, attr):
    return getattr(obj, attr)
  return functools.reduce(subGetAttr, [obj] + attr.split("."))

def appendOfferIDsToArr(op, offerIDarr, address):
  makerIDattr = "success.offer.offer.offer_id.int64"
  takerIDattr = "success.offers_claimed"
  try:
    offerID = getAttr(op.manage_sell_offer_result, makerIDattr)
    if(len(str(offerID)) > 10):
      pprint(offerID)
      pprint(op)
      pprint(op.to_xdr())
  except AttributeError:
    try:
      offerID = getAttr(op.manage_buy_offer_result, makerIDattr)
    except AttributeError:
      try:
        offerID = resolveTakerOffer(getAttr(op.manage_sell_offer_result, takerIDattr), offerIDarr, address)
      except AttributeError:
        offerID = resolveTakerOffer(getAttr(op.manage_buy_offer_result, takerIDattr), offerIDarr, address)
  return offerIDarr.append(offerID)

def resolveTakerOffer(offersClaimed, offerIDarr, address):
  IDattr = "offer_id.int64"
  offerID = 0
  for trades in offersClaimed:
    try:
      offerID = getOfferIDfromContraID(getAttr(trades.order_book, IDattr), address)
    except AttributeError:
      try:
        offerID = getOfferIDfromContraID(getAttr(trades.liquidity_pool, IDattr), address)
      except AttributeError:
        offerID = getOfferIDfromContraID(getAttr(trades.v0, IDattr), address)
    offerIDarr.append(offerID)
  return offerID

def getOfferIDfromContraID(offerID, address):
  requestAddr = f"{HORIZON_INST}/offers/{offerID}/trades?{MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for trades in ledger["_embedded"]["records"]:
      if(trades["counter_account"] == address):
        return int(trades["counter_offer_id"])
      elif(trades["base_account"] == address):
        return int(trades["base_offer_id"])
    ledger = getNextLedgerData(ledger)

def getTradeData(offerID, address):
  try:
    int(offerID)
  except ValueError: 
    return 0
  tradeData = {}
  type = ""
  value = shares = Decimal("0")
  requestAddr = f"{HORIZON_INST}/offers/{offerID}/trades?{MAX_SEARCH}"
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
    tradeData["fillDate"] = pandas.to_datetime(trades["ledger_close_time"])
    ledger = getNextLedgerData(ledger)
  tradeData["shares"] = shares
  tradeData["value"] = value
  tradeData["offerID"] = offerID
  tradeData["type"] = type
  return tradeData if value else {"type": 0}

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
  combined["type"] = "covered" if originTradeData else "uncovered"
  combined["asset"] = tradeData["asset"]
  combined["originTradeDate"] = originTradeData["fillDate"] if originTradeData else 0
  combined["originTradeShares"] = adjustNumSharesForStockSplits(
    originTradeData["shares"],
    originTradeData["originTradeDate"],
    originTradeData["asset"].code
  ) if originTradeData else 0
  combined["originTradeValue"] = originTradeData["value"] if originTradeData else 0
  combined["exitTradeShares"] = tradeData["shares"]
  combined["exitTradeValue"] = tradeData["value"]
  combined["exitTradeDate"] = tradeData["fillDate"]
  return combined

def getTradePNL(combinedTradeData, address):
  match combinedTradeData["type"]:
    case "covered":
      return getCoveredTradePNL(combinedTradeData)
    case "uncovered":
      return getUncoveredTradePNL(combinedTradeData, address)

def getCoveredTradePNL(data):
  if(data["originTradeShares"] == data["exitTradeShares"]):
    return(data["originTradeValue"], data["exitTradeValue"] - data["originTradeValue"])
  elif(data["originTradeShares"] > data["exitTradeShares"]):
    entryPrice = data["originTradeShares"] / data["originTradeValue"]
    originBasisAdj = data["exitTradeShares"] * entryPrice
    return(originBasisAdj, data["exitTradeValue"] - originBasisAdj)
  else:
    sys.exit("todo: test on live data, see if can combine")

def getUncoveredTradePNL(data, addr):
  historicPositions = getHistoricPositionsFromAccountData(addr)
  
  # code on interface as paging_token from sending shares initially for positional close
  historicPositions = getHistoricPositionsDataFromBTdistributionMemos(address)
  
  sharesBought = adjustNumSharesForStockSplits(a, b, data[1].code)
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

# purchaseBasisAdj
# PNL

def getWashSaleOfferIDs(address):
  return 1
  
def getHistoricPositions(address):
  historicPositions = {}
  
  return distributionPagingTokensMappedToHistoricData

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
form8949forAccount("GC2EUCIRRDSVMTG5IG3X7NJZPWQLXMJRXV6REUAF3ALOK2GPL6GC625J")
#fetchInvestorPreExistingPositionsForAsset("GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML", "DEMO")






