import sys
sys.path.append("../")
from globals import *
import functools, threading #todo: threads -> global
from taxTestingData import *

# offerIDsMappedToChiefMemosForAccount = {} #override external tax data

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
washSaleAdjStart = taxYearStart - pandas.DateOffset(days = WASH_SALE_DAY_RANGE)
washSaleAdjCutoff = taxYearEnd + pandas.DateOffset(days = WASH_SALE_DAY_RANGE)

def bulkOutput():
  MICRlines = open("access_me.csv").readlines().split("|")
  threads = []
  for addresses, i in enumerate(MICRlines[0]):
    form8949forAccount(addresses)
    threads.append(
        threading.Thread(
          target = form8949forAccount,
          args = (addresses,)
        )
      )
    threads[i].start().join()

def form8949forAccount(address):
  # taxableSales = washSaleReferenceList = []
  # TODO: Impliment dict caching w/ MICR: start at last known offerID timestamp
  # offerIDsMappedToChiefMemosForAccount = getOfferIDsMappedToChiefMemosForAccount(address) 
  for offerIDs, memoOpeningInstr in offerIDsMappedToChiefMemosForAccount.items():
    offerIDtradeData = getTradeData(offerIDs, address)
    if(offerIDtradeData[1] == "sell"): # This is a closing offer
      openingOfferID = offerIDsMappedToChiefMemosForAccount[offerIDs]
      openingTradeData = getTradeData(memoOpeningInstr, address)
      combined = combineTradeData(offerIDtradeData[2], openingTradeData)
      if(combined[0] == "covered"):
        combined += getPNLfromCombinedCoveredTrade(combined)
      else:
        combined += getPNLfromCombinedUncoveredTrade(combined, address)
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
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for txns in ledger["_embedded"]["records"]:
      if(txns["source_account"] == address):
        resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
        for ops in resultXDR.result.results:
          ops = ops.tr
          if(ops.manage_buy_offer_result or ops.manage_sell_offer_result):
            offerIDarr = []
            appendOpTrOfferIDsToArr(ops, offerIDarr, address)
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

class NoOffersClaimed(Exception):
  def __init__(self, message = "Offer deleted"):
    super(NoOffersClaimed, self).__init__(message)

def appendOpTrOfferIDsToArr(op, offerIDarr, address):
  makerIDattr = "success.offer.offer.offer_id.int64"
  try:
    offerID = getAttr(op.manage_sell_offer_result, makerIDattr)
  except AttributeError:
    try:
      offerID = getAttr(op.manage_buy_offer_result, makerIDattr)
    except AttributeError:
      try:
        offerID = resolveTakerOffer(op.manage_sell_offer_result.success, offerIDarr, address)
      except AttributeError:
        try:
          offerID = resolveTakerOffer(op.manage_buy_offer_result.success, offerIDarr, address)
        except AttributeError:
          sys.exit(f"Failed to resolve offerID in\n{op}\n")
  return offerIDarr.append(offerID)

def resolveTakerOffer(taker, offerIDarr, address):
  takerIDattr = "offer.offer.offer_id.int64"
  try:
    print(getAttr(taker, takerIDattr))
    sys.exit(1)
    return getOfferIDfromContraID(getAttr(taker, takerIDattr), address)
  except AttributeError:
    try:
      return appendOfferIDsFromClaimedContras(taker.offers_claimed, offerIDarr, address, taker)
    except NoOffersClaimed:
      return 0

def getOfferIDfromContraID(offerID, address):
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for trades in ledger["_embedded"]["records"]:
      try:
        if(trades["counter_account"] == address):
          return int(trades["counter_offer_id"])
        elif(trades["base_account"] == address):
          return int(trades["base_offer_id"])
      except KeyError:
        sys.exit(f"No offerID found:\n{trades}")
    ledger = getNextLedgerData(ledger)
  sys.exit(f"No source trade found: {offerID}")

def appendOfferIDsFromClaimedContras(offersClaimed, offerIDarr, address, t):
  lastTrade = offersClaimed[-1:]
  IDattr = "offer_id.int64"
  for trades in offersClaimed:
    try:
      offerID = getOfferIDfromContraID(getAttr(trades.order_book, IDattr), address)
    except AttributeError:
      try:
        offerID = getOfferIDfromContraID(getAttr(trades.liquidity_pool, IDattr), address)
      except AttributeError:
        try:
          offerID = getOfferIDfromContraID(getAttr(trades.v0, IDattr), address)
        except AttributeError:
          sys.exit(f"Atomic swap contra discovery failed:\n{offersClaimed}")
    if(trades != lastTrade):
      offerIDarr.append(offerID)
  try:
    return offerID
  except UnboundLocalError:
    raise NoOffersClaimed

def getTradeData(offerID, address):
  try:
    int(offerID)
  except ValueError: 
    return 0
  tradeData = {}
  type = ""
  value = shares = Decimal("0")
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
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
    tradeData["finalExecutionDate"] = pandas.to_datetime(trades["ledger_close_time"])
    ledger = getNextLedgerData(ledger)
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

def getPNLfromCombinedCoveredTrade(data):
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

# acct data entry format for prexisting basis:
# later you can update with numShares - amoutn used
# can reference data op paging num? 

def getPNLfromCombinedUncoveredTrade(data, addr):
  historicPositions = getHistoricPositionsFromAccountData(addr)
 


# for address, assetCode, purchaseDate, shares, basis in lines.split("|"):
  
  # assetCode,
  # pandas.to_datetime(f"{purchaseDate}T20:00:00Z"),
  # Decimal(shares),
  # Decimal(basis)
  # # suggestion: account data values 
        
        
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

# How flow works (assume semi-honest user since it's their taxes returns at stake):
# BT_DISTRIBUTOR sends account [numShares] stock with memo:
#   [price]||uncovered||DWAC:[coveredDate]||
# Account does manage_data( distriubtion paging_token: [assetCode]:[numShares]:[price]:2003-6-9 ) locally
#     case distributionMemo:
#       match covered (has date)    -> paging_token: [assetCode]:[numShares]:[price]:2003-6-9
#       match uncovered             -> paging_token: [assetCode]:[numShares]:uncovered:
#       match DWAC                  -> paging_token: [assetCode]:[numShares]:DWAC:[brokerDate]
#   DWAC transfers may not include the basis - brokers can send it separately in a month
#   Send user 0.0000001XLM txn w/ memo [paging_token]:[DWAC basis] so they can update
#   Currently room in memo for stocks priced under 1M/share, which should be fine
#   If becomes probalmatic, we can front truncate paging_token by a few numbers
# Use paging_token as offerID in wallet when directing closing instructions
# When selling with reference to trade, manage_data ( paging_token: [numShares - sharesSold]... )

def getHistoricPositions(address):
  historicPositions = {}
  distributionPagingTokensMappedToHistoricData = getDistributionPagingTokensMappedToHistoricData(address)
  return distributionPagingTokensMappedToMemos

def getDistributionPagingTokensMappedToMemos(address):
  distributionPagingTokensMappedToHistoricData = {}
  requestAddr = f"https://{HORIZON_INST}/accounts/{address}/payments?limit={MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for payments in ledger["_embedded"]["records"]:
      try:
        BTasset = payments["asset_issuer"] == BT_ISSUER
      except KeyError:
        continue
      if(BTasset and payments["from"] == BT_DISTRIBUTOR):
        txnAddr = payments["_links"]["transaction"]["href"]
        txnData = requests.get(txnAddr).json()
        try:
          memo = txnData["memo"]
        except KeyError:
          memo = "42.00:2009-9-9"
          memo = "DWAC:2009-9-9"
          #memo = "42.00:"
          # continue
        memo = memo.split(":")
        price = memo[0]
        match price:
          case "uncovered":
            date = ""
          case "DWAC":
            date = memo[1] if memo[1] else txnData["created_at"].split("T")[0]
          case other:
            date = memo[1]
        
        assetCode = payments["asset_issuer"]
        numShares = payments["amount"]
        pagingToken = payments["paging_token"]
        distributionData = ()
        distributionPagingTokensMappedToHistoricData[pagingToken] = distributionData
    #  [price]||uncovered||DWAC:[coveredDate]||
    ledger = getNextLedgerData(ledger)
  return distributionPagingTokensMappedToHistoricData
  #date@price -> paging_token: [assetCode]:[numShares]:[price]:2003-6-9
#       match uncovered             -> paging_token: [assetCode]:[numShares]:uncovered:
#       match DWAC                  -> paging_token: [assetCode]:[numShares]:DWAC:[txnDate]

print(getHistoricPositions("GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML"))
sys.exit()

# paging_token: basis
def getDWACbasisFromAccountData(addr):
  data = getAccountCustomLedgerData(addr)
  historicPositionsCUSIPsMappedToBasisData = {}
  for key, value in data.items():
    if(isCUSIP(key)):
      historicPositionsCUSIPsMappedToBasisData[key] = value
  return historicPositionsCUSIPsMappedToBasisData

# [succeedingOfferID]: [lossDissallowedFromPriorTrade]
def getWashSalesFromAccountData(addr):
  data = getAccountCustomLedgerData(addr)
  succeedingOffersMappedToBasisAdjustments = {}
  for key, value in data.items():
    if(key in offerIDsMappedToChiefMemosForAccount.keys()):
      succeedingOffersMappedToBasisAdjustments[key] = value
  return succeedingOffersMappedToBasisAdjustments

def getAccountCustomLedgerData(addr):
  requestAddr = f"https://{HORIZON_INST}/accounts/{addr}"
  try:
    return requests.get(requestAddr).json()["data"]
  except KeyError:
    return 0

def getUncoveredBasis(data):
  # you can't get the basis for uncovered shares ?
  return 1

def adjustNumSharesForStockSplits(numShares, purchaseTimestamp, queryAsset):
  splitsDict = getSplitsDict(queryAsset)
  for splitTimestamps, splitRatios in splitsDict.items():
    if(purchaseTimestamp < splitTimestamps):
      numShares = numShares * splitRatios
  return numShares

def getSplitsDict(queryAsset):
  splitsDict = {}
  try:
    data = loadTomlData(BT_STELLAR_TOML)
    for currencies in data["CURRENCIES"]:
      assetCode = getAssetCodeFromTomlLink(currencies["toml"])
      if(assetCode == queryAsset):
        data = loadTomlData(currencies["toml"])
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
  
  
  
  # WHEN WE HAVE A WASH SALE:
  # we have to update the cost basis for the succeeding trade
  # HOW TO UPDATE SUCCEEDING COST BASIS? 
  #    - account ledger value:pair entries mapping offer ID to new basis 
  #        - if(lookup if offerID in mappingItems ):
  #          -  basis = offerBasis + adj.
  #        - else:
  #          -  basis = offerBasis
  #      - requires user to publish wash sale value:pair the moment they execute the wa
  #      - as such, must be implimented via wallet on the order level 
  #        - basically not going to happed for users with hardware wallets, but neither wi
  #          - so then everything works with SH as long as they use our platform 
  #            - this should be fine as long as everything is open-source
  #      - can remove mapping once wash sale pos. closed 
  #        - must wait 30 days if sold at loss 
  #        - could automatically be done in  wallet background next time they login after 1mo. mark (if loss)
  #          - requires computation of all open positions and potentials washes when opening wallet, which could be compute heavy
  #          - could slow down succeeding order execution
  #PROS
  #            - pretty minimal calculation if you cache recent potential wash sales in wallet
  #            - only 1 more txn op which isn't a huge deal 
  #CONS
  #            - requires new offerID to post {succeedingOfferID: baseAdjustment<-lossDissallowedFromPriorTrade} value pair 
  #            - so requires a reply from Horizon with offerID | contra lookup and then sending new txn 
  #              - SH user could accidentally quit wallet after sale
  #              - new value txn would need to be cached and sent at next wallet launch
  #              - when possible: could prevent user from closing wallet until new value mapped
  #                - or just send the new value mapping txns intentionally BEFORE displaying order confirmation to user with extremely high fee to ensure immediate acceptance
  #    - 
  #    - 
  #    - 
  #    - 
  

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
print(getHistoricPositionsFromAccountData("GAJ4BSGJE6UQHZAZ5U5IUOABPDCYPKPS3RFS2NVNGFGFXGVQDLBQJW2P"))
# print(adjustSharesBoughtForStockSplits(Decimal("100"), date, "DEMO"))
#form8949forAccount("GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG")
#fetchInvestorPreExistingPositionsForAsset("GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML", "DEMO")






