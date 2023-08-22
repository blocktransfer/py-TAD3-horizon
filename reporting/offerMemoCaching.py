import sys
sys.path.append("../")
from globals import *

from cacheHelper import *

def updateCache(type="offer-memos"):
  currHeight = getRefBlock()
  cacheHeight, cache = readCache(type)
  for pubKeys in getAllPublicKeys():
    print(f"Querying new offers for {pubKeys}")
    updateCacheFromHeightForFilledOfferMemosForPK(cache, cacheHeight, pubKeys)
  archiveCache(type)
  saveCache(cache, type, currHeight)

def updateCacheFromHeightForFilledOfferMemosForPK(cache, cacheHeight, pubKey):
  ledger = requestXLM(f"accounts/{pubKey}/transactions")
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for txns in records:
      if(txns["source_account"] != pubKey):
        continue
      if(txns["ledger"] <= cacheHeight):
        continue
      txResults = TransactionResult.from_xdr(txns["result_xdr"]).result.results
      if(not txResults):
        continue
      for ops in txResults:
        op = ops.tr
        if(op.manage_buy_offer_result or op.manage_sell_offer_result):
          for offerIDs in getListOpOfferIDreturnsMultipleForMarketOrder(op, pubKey):
            if(offerIDs not in cache):
              cache[offerIDs] = getMemoFromTransaction(txns)
    links, records = getNextLedgerData(links)

def isMakerTrade(successfulOfferObj):
  return successfulOfferObj.offer.offer

def getMakerOfferID(successfulOfferObj):
  return [successfulOfferObj.offer.offer.offer_id.int64]

def getListOpOfferIDreturnsMultipleForMarketOrder(op, pubKey):
  offer = (
    op.manage_sell_offer_result
    if op.manage_sell_offer_result
    else op.manage_buy_offer_result
  ).success 
  if(isMakerTrade(offer)):
    return getMakerOfferID(offer)
  else:
    marketOrderCounterTrades = offer.offers_claimed
  return getSyntheticTakerIDs(marketOrderCounterTrades, pubKey)

def getSyntheticTakerIDs(counterTrades, pubKey):
  tradeTypes = ["order_book", "liquidity_pool", "v0"]
  syntheticTakerIDs = []
  for trades in counterTrades:
    for types in tradeTypes:
      contraType = getattr(trades, types, None)
      if(contraType):
        contraID = contraType.offer_id.int64
    syntheticTakerIDs.append(
      getOfferIDforPKfromContraID(contraID, pubKey)
    )
  return syntheticTakerIDs

def getOfferIDforPKfromContraID(contraID, pubKey):
  ledger = requestXLM(f"offers/{contraID}/trades")
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for trades in records:
      if(trades["counter_account"] == pubKey):
        return int(trades["counter_offer_id"])
      elif(trades["base_account"] == pubKey):
        return int(trades["base_offer_id"])
    links, records = getNextLedgerData(links)


updateCache()
