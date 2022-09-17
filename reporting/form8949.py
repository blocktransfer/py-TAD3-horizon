import sys
sys.path.append("../")
from globals import *
from taxTestingData import *

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
  accountTrades = []
  #offerIDsMappedToChiefMemosForAccount = getofferIDsMappedToChiefMemosForAccount(address) # TODO: Impliment some kind of caching here (associated with MICR?)
  for offerIDs in offerIDsMappedToChiefMemosForAccount:
    sale = getSellTradeData(offerIDs, address)
    if(sale and washSaleAdjStart <= sale[2]["finalExecutionDate"] <= washSaleAdjCutoff):
      pprint(sale)
      matchOfferID = offerIDsMappedToChiefMemosForAccount[offerIDs]
      origin = getBuyTradeData(matchOfferID, address)
      combined = combineTradeData(sale[2], origin)
      if(combined[0] == "covered"):
        combined += getCoveredBasisAndProceeds(combined)
      else:
        # - pull pii record which has association for uncovered securities or pre-existing cost basis
        combined += getUncoveredBasisAndProceeds(combined)
      accountTrades.append(combined)
  adjustedTrades = adjustForWashSales(accountTrades, address, offerIDsMappedToChiefMemosForAccount)
  # mergedTrades = mergeForVARIOUS(adjustedTrades) ? or just do by orderID?
  finalFormData = placeFields(adjustedTrades)
  #export to 8949 PDF(s)

def getOfferIDsMappedToChiefMemosForAccount(address):
  # offerIDsMappedToChiefMemosForAccount = {}
  requestAddr = f"https://{HORIZON_INST}/accounts/{address}/transactions?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for txns in blockchainRecords:
      if(txns["source_account"] != address):
        continue
      resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
      for ops in resultXDR.result.results:
        offerIDarr = []
        appendOfferIDfromTxnOpToBaseArr(ops, offerIDarr, address)
        for offerIDs in offerIDarr:
          if(offerIDs and offerIDs not in offerIDsMappedToChiefMemosForAccount.keys()):
            try:
              memo = txns["memo"]
            except KeyError:
              memo = ""
            offerIDsMappedToChiefMemosForAccount[offerIDs] = memo
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("\u0026", "&")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  return 1 #offerIDsMappedToChiefMemosForAccount

def appendOfferIDfromTxnOpToBaseArr(op, offerIDarr, address):
  try:
    offerID = op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64
  except AttributeError:
    try:
      offerID = op.tr.manage_buy_offer_result.success.offer.offer.offer_id.int64
    except AttributeError:
      try:
        taker = op.tr.manage_sell_offer_result.success
        offerID = addClaimedOffersToIDarr(taker.offers_claimed, offerIDarr) if len(taker.offers_claimed) else getOfferIDfromContraID(taker.offer.offer.offer_id.int64, address)
      except AttributeError:
        try:
          taker = op.tr.manage_buy_offer_result.success
          offerID = addClaimedOffersToIDarr(taker.offers_claimed, offerIDarr) if len(taker.offers_claimed) else getOfferIDfromContraID(taker.offer.offer.offer_id.int64, address)
        except:
          sys.exit(f"Failed to resolve offerID in\n{op}")
  return offerIDarr.append(offerID)

def addClaimedOffersToIDarr(takerResult, offerIDarr):
  for trades in takerResult:
    try:
      offerID = getOfferIDfromContraID(trades.order_book.offer_id.int64, address)
    except AttributeError:
      try:
        offerID = getOfferIDfromContraID(trades.liquidity_pool.offer_id.int64, address)
      except AttributeError:
        try:
          offerID = getOfferIDfromContraID(trades.v0.offer_id.int64, address)
        except:
          sys.exit("Atomic swap contra discovery failed")
    offerIDarr.append(offerID)
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
        sys.exit(f"Error generating syntheic ID - check paging token")
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  sys.exit(f"Could not find offerID from Omnibus Contra #{offerID}")

def getBuyTradeData(offerID, address):
  if(not offerID):
    return 0
  tradeData = {}
  totalFiatCost = totalSharesPurchased = Decimal("0")
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      baseAsset = getBaseAsset(trades)
      baseAssetFiat = isFiat(baseAsset)
      counterAsset = getCounterAsset(trades)
      counterAssetFiat = isFiat(counterAsset)
      # Expect one asset is fiat
      if(trades["base_account"] == address):
        tradeData["asset"] = counterAsset
        if(baseAssetFiat):
          totalFiatCost += Decimal(trades["base_amount"])
          totalSharesPurchased += Decimal(trades["counter_amount"])
        if(counterAssetFiat):
          return 0
      elif(trades["counter_account"] == address):
        tradeData["asset"] = baseAsset
        if(counterAssetFiat):
          totalFiatCost += Decimal(trades["counter_amount"])
          totalSharesPurchased += Decimal(trades["base_amount"])
        if(baseAssetFiat):
          return 0
    tradeData["finalExecutionDate"] = pandas.to_datetime(trades["ledger_close_time"])
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  tradeData["shares"] = totalSharesPurchased
  tradeData["value"] = totalFiatCost
  return (offerID, "buy", tradeData) if totalFiatCost else 0

def getSellTradeData(offerID, address):
  if(not offerID):
    return 0
  tradeData = {}
  totalFiatProceeds = totalSharesSold = Decimal("0")
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      baseAsset = getBaseAsset(trades)
      baseAssetFiat = isFiat(baseAsset)
      counterAsset = getCounterAsset(trades)
      counterAssetFiat = isFiat(counterAsset)
      if(trades["base_account"] == address):
        tradeData["asset"] = counterAsset
        if(counterAssetFiat):
          totalFiatProceeds += Decimal(trades["counter_amount"])
          totalSharesSold += Decimal(trades["base_amount"])
        if(baseAssetFiat):
          return 0
      elif(trades["counter_account"] == address):
        tradeData["asset"] = baseAsset
        if(baseAssetFiat):
          totalFiatProceeds += Decimal(trades["base_amount"])
          totalSharesSold += Decimal(trades["counter_amount"])
        if(counterAssetFiat):
          return 0
    tradeData["finalExecutionDate"] = pandas.to_datetime(trades["ledger_close_time"])
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  tradeData["shares"] = totalSharesSold
  tradeData["value"] = totalFiatProceeds
  return (offerID, "sell", tradeData) if totalFiatProceeds else 0

def getBaseAsset(trade):
  try:
    return Asset(trade["base_asset_code"], trade["base_asset_issuer"])
  except KeyError:
    return Asset.native()

def getCounterAsset(trade):
  try:
    return Asset(trade["counter_asset_code"], trade["counter_asset_issuer"])
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
  assert(tradeData["asset"] == originTradeData["asset"])
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

def getCoveredBasisAndProceeds(combinedTradeData):
  sharesBought = adjustSharesBoughtForStockSplits(data[3], data[2], data[1].code)
  sharesSold = data[5]
  purchaseBasis = data[4]
  saleProceeds = data[6]
  if(sharesBought == sharesSold):
    return(purchaseBasis, saleProceeds, saleProceeds - purchaseBasis)
  elif(sharesBought > sharesSold):
    purchasePrice = sharesBought / purchaseBasis
    purchaseBasisAdj = sharesSold * purchasePrice
    return(purchaseBasisAdj, saleProceeds, saleProceeds - purchaseBasisAdj)
  else:
    sys.exit("todo: test on live data")

def getUncoveredBasisAndProceeds(combinedTradeData):
  # pull basis from data 
  # ? sharesBought = adjustSharesBoughtForStockSplits(data[3], data[2], data[1].code)
  sharesSold = data[5]
  purchaseBasis = data[4]
  saleProceeds = data[6]
  return (purchaseBasis, saleProceeds, saleProceeds - purchaseBasis) ###todo

def adjustSharesBoughtForStockSplits(numShares, purchaseTimestamp, queryAsset):
  try:
    requestAddr = "https://blocktransfer.io/.well-known/stellar.toml"
    data = toml.loads(requests.get(requestAddr).content.decode())
    for currencies in data["CURRENCIES"]:
      if(currencies["toml"][32:-5] == queryAsset):
        print(currencies["toml"][-(5+len(queryAsset)):-5])
        data = toml.loads(requests.get(currencies["toml"]).content.decode())
        pprint(data)
        spltData = data["CURRENCIES"][0]["splits"].split("|")
        pprint(splitData)
        for splits in splitData:
          print(splits[0])
          print(splits[4])
          print(splits[-10:])
          print("\n")
          
        break
  except KeyboardInterrupt:
    sys.exit(f"Failed to lookup split info for {queryAsset}")
  return data
  
  return numShares ###todo

date = pandas.to_datetime("2020-1-15")
# T00:00:00Z
a = {'CURRENCIES': [{'anchor_asset': '922908355-test',
                 'anchor_asset_type': 'stock',
                 'attestation_of_reserve': 'https://blocktransfer.io/board-resolutions/demo.pdf',
                 'code': 'DEMO',
                 'conditions': 'Register at investors.blocktransfer.io for '
                               'applicable terms.',
                 'desc': 'This is an example stock used interally for product '
                         'demos and development.',
                 'display_decimals': 7,
                 'image': 'https://blocktransfer.io/img/demo.png',
                 'is_asset_anchored': True,
                 'is_unlimited': True,
                 'issuer': 'GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7',
                 'name': 'Example Security',
                 'redemption_instructions': 'Submit a DWAC transfer request '
                                            'to/from DRS through your broker.',
                 'regulated': False,
                 'splits': '1 to 5 effective 2021-4-20|3 to 2 effective '
                           '2021-10-9|2 to 1 effective 2022-1-1',
                 'status': 'test'}]}
z = "https://blocktransfer.io/assets/DEM3482904932O.toml"
print(z[-(5+len("DEM3482904932O")):-5])
b = a["CURRENCIES"][0]["splits"].split("|")
pprint(type(b))
print(b)
pprint(adjustSharesBoughtForStockSplits(Decimal("100"), date, "DEMO"))


def adjustForWashSales(accountTrades, address, offerIDsMappedToChiefMemosForAccount):
  adjustedTrades = []
  yearEndWashSaleWatchlist = washSaleWatchlist = {}
  for trades in accountTrades:
    
    purchaseTimestamp
    
    
    if(saleTimestamp < taxYearStart + pandas.DateOffset(days = WASH_SALE_DAY_RANGE)):
      if(saleCUSIP in yearEndWashSaleWatchlist.keys()):
        # compare the dates
        a=1
        # adjustments/merge as needed
        
      washSaleWatchlist[saleCUSIP] = trades
        
      
      matchOfferID = offerIDsMappedToChiefMemosForAccount[offerID]
      adjustForModifiedBasisFromTwoYearsPrior(purchaseOfferID, address, offerIDsMappedToChiefMemosForAccount)
      return ans
    
    
    return tradeData
    
  return adjustedTrades

def adjustForModifiedBasisFromTwoYearsPrior(purchaseOfferID, address, offerIDsMappedToChiefMemosForAccount):
  adjustedTrades = []
  return 1
  
  origin = getBuyTradeData(matchOfferID, address)
  combined = combineTradeData(sale[2], origin)
  if(combined[0] == "covered"):
    (basis, proceeds) = getCoveredBasisAndProceeds(combined)
    combined += (basis, proceeds, proceeds - basis)
  ss.append(combined) 

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
form8949forAccount(BT_ISSUER)
