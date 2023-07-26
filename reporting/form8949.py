import sys
sys.path.append("../")
from globals import *

# debug: 
# USDC_ASSET = Asset("TERN", "GDGQDVO6XPFSY4NMX75A7AOVYCF5JYGW2SHCJJNWCQWIDGOZB53DGP6C")

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week
# washSaleAdjStart = taxYearStart - pandas.DateOffset(days = WASH_SALE_DAY_RANGE)
# washSaleAdjCutoff = taxYearEnd + pandas.DateOffset(days = WASH_SALE_DAY_RANGE)

def bulkOutput():
  accounts = getAllPublicKeys()
  numAccounts = len(accounts)
  i = 0
  for account in accounts:
    i += 1
    print(f"Executing export for {account} ({i}/{numAccounts})")
    form8949(account)


def form8949(queryAccount):
  allTrades = []
  offerIDsMappedToChiefMemos = getOfferIDsMappedToChiefMemosFromCache()
  for offerIDs, memos in offerIDsMappedToChiefMemos.items():
    requestAddr = f"{HORIZON_INST}/offers/{offerIDs}/trades"
    memo = memos.split("|")
    instructions = memo[0]
    address = memo[1]
    if(address == queryAccount):
      offerTradeData = getTradeData(offerIDs, address)
      if(offerTradeData["type"] == "out"):
        if(tradeInTaxableYear(offerTradeData)):
          originTradeData = getTradeData(instructions, address)
          combinedTradeData = combineTradeData(offerTradeData, originTradeData)
          exportData = getTradePNL(combinedTradeData, instructions, address)
          
          allTrades.append(exportData)
  pprint(allTrades)
  # finalFormData = placeFieldsplaceFields(adjustedTrades)
  # exportForm8949(finalFormData) # mergeForVarious

# -> investor app diction
# b = len("1234567890123456")
# if(b < 16):
#   offerID
# elif(b < 19)
#   synthetic offerID
# else: 
#   paging token

def tradeInTaxableYear(tradeData):
  return taxYearStart <= tradeData["fillDate"] < taxYearEnd

def getTradeData(offerID, address):
  tradeData = {"type": 0}
  type = ""
  value = shares = Decimal("0")
  try:
    url = f"{HORIZON_INST}/offers/{int(offerID)}/trades?{MAX_SEARCH}"
  except ValueError:
    return tradeData
  ledger = requests.get(url).json()
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for trades in records:
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
    links, records = getNextLedgerData(links)
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
  combined = { "asset": tradeData["asset"] }
  validOrigin = originTradeData["type"]
  combined["originOfferID"] = originTradeData["offerID"] if validOrigin else 0
  combined["originTradeDate"] = originTradeData["fillDate"] if validOrigin else 0
  combined["originTradeShares"] = adjustNumSharesForStockSplits(
    originTradeData["shares"],
    originTradeData["fillDate"],
    originTradeData["asset"].code
  ) if validOrigin else 0
  combined["originTradeValue"] = originTradeData["value"] if validOrigin else 0
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
  
  washSaleAdjustment = Decimal("0")
  
  if fill["originOfferID"]
    washSaleOfferIDsMappedToAdjustments = getWashSaleOfferIDsMappedToAdjustments()
    washSaleAdjustment = [fill["originOfferID"]]
  
  scaleDissalowedLossByPositionSize(washSaleAdjustment)
  
  fill["washSaleAdjustment"] = washSaleAdjustment
  fill["PNL"] -= fill["washSaleAdjustment"]

  return fill

def getOriginDataFromPagingToken(opPagingToken, address):
  originDistributionData = {}
  requestAddr = f"{HORIZON_INST}/operations/{opPagingToken}"
  try:
    opData = requests.get(requestAddr).json()
    transactionAddr = opData["_links"]["transaction"]["href"]
  except KeyError:
    return {"badOriginData": True}
  try:
    memo = requests.get(transactionAddr).json()["memo"]
  except KeyError:
    memo = "uncovered|" 
  # memo format: {price/"uncovered"/"DWAC"}|{buyDate/""}
  memo = memo.split("|")
  match memo[0]:
    case "uncovered":
      legacyPrice = Decimal("0")
    case "DWAC":
      try:
        legacyPrice = Decimal(getAccountDataDict(BT_DISTRIBUTOR)[f"DWAC|{opPagingToken}"])
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

# individual account data should not be responsible for tracking wash sale adjusts;
# investor only specifies sale lot
def basisFromAccountData(addr):
  data = getAccountDataDict(addr)
  historicPositionsCUSIPsMappedToBasisData = {}
  for key, value in data.items():
    if(isCUSIP(key)):
      historicPositionsCUSIPsMappedToBasisData[key] = value
  return historicPositionsCUSIPsMappedToBasisData
def getWashSalesFromAccountData(addr):
  data = getAccountDataDict(addr)
  succeedingOffersMappedToBasisAdjustments = {}
  for key, value in data.items():
    if(key in offerIDsMappedToChiefMemosForAccount.keys()):
      succeedingOffersMappedToBasisAdjustments[key] = value
  return succeedingOffersMappedToBasisAdjustments
def adjustAllTradesForWashSales(combinedData, address):
  matchOfferID = offerIDsMappedToChiefMemosForAccount[offerID]
  adjustForModifiedBasisFromTwoYearsPrior(purchaseOfferID, address, offerIDsMappedToChiefMemosForAccount)
def adjustForModifiedBasisFromTwoYearsPrior(purchaseOfferID, address, offerIDsMappedToChiefMemosForAccount):
  #origin = getBuyTradeData(matchOfferID, address)
  if(combined[0] == "covered"):
    (basis, proceeds) = getCoveredBasisAndProceeds(combined)
    combined += (basis, proceeds, proceeds - basis)
def filterTradesToTaxablePeriod(finalTrades):
  return washSaleAdjStart <= sale[2]["fillDate"] <= washSaleAdjCutoff # fix

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

# DEF Separate PRINT FUNCT
# https://medium.com/@zwinny/filling-pdf-forms-in-python-the-right-way-eb9592e03dba
# https://www.blog.pythonlibrary.org/2018/05/22/filling-pdf-forms-with-python/
# https://akdux.com/python/2020/10/31/python-fill-pdf-files/
# https://pypdf2.readthedocs.io/en/latest/user/forms.html#filling-out-forms
# https://pypi.org/project/fillpdf/
# https://www.securexfilings.com/wp-content/uploads/2013/04/sched13d.pdf
form8949("GC5TUPFLOXCINDYHQVYYLLVYP6GKHT65ELB2Q2WLFTGN63YYIXPQTDFJ")



# Method for CBs:
# Scan account for claim CB txn
#   in general, user wallet automatically claims avaliable CBs which can be restircted stock, stock grants, or potentially options or something more complex from a smart contract in the future
# If the transfer comes from the BT_DISTRIBUTOR account, then you know it was pre-existing shares, no tax impact
# If the transfer was from one of the issuer offering.holding accounts, then you know it was from newly-issued shares, no tax impact
# If it was from the issuer employee.holdings account (or anywhere else?) then you know that it was taxable income
# You can still use the CB memos to retrive share compensation data before claiming avaliable stock, removing the CB ID from the network (perpetual centralized caching is bad)