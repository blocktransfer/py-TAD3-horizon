import sys
sys.path.append("../")
from globals import *

from cacheHelper import *

def getLifetimeOfferMemosForIndvPK(pubKey):
  offerMemos = {}
  ledger = requestXLM(f"accounts/{pubKey}/transactions")
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for txns in records:
      if(txns["source_account"] == pubKey):
        txResults = getTxnResFromXDR(txns["result_xdr"])
        for ops in results:
          offer = getSuccessfulOfferObjFromTxnOp(ops)
          for offerIDs in getListOfferIDsForOfferObj(offer, pubKey):
            offerMemos[offerIDs] = getMemoFromTransaction(txns)
    links, records = getNextLedgerData(links)
  return offerMemos

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
      txResults = getTxnResFromXDR(txns["result_xdr"])
      for ops in txResults:
        offer = getSuccessfulOfferObjFromTxnOp(ops)
        for offerIDs in getListOfferIDsForOfferObj(offer, pubKey):
          offerMemos[offerIDs] = getMemoFromTransaction(txns)
    links, records = getNextLedgerData(links)

def getTxnResFromXDR(resultXDR):
  txnRes = TransactionResult.from_xdr(resultXDR).result.results
  return txnRes if txnRes else []

def getSuccessfulOfferObjFromTxnOp(op):
  op = op.tr
  return (
    op.manage_sell_offer_result
    if op.manage_sell_offer_result
    else op.manage_buy_offer_result
  ).success

def isMakerTrade(successfulOfferObj):
  return successfulOfferObj.offer.offer

def getMakerOfferID(successfulOfferObj):
  return [successfulOfferObj.offer.offer.offer_id.int64]

def getListOfferIDsForOfferObj(offer, pubKey):
  if(not offer):
    return []
  elif(isMakerTrade(offer)):
    return getMakerOfferID(offer)
  else:
    marketOrderCounterTrades = offer.offers_claimed
  return getTakerOfferIDs(marketOrderCounterTrades, pubKey)

def getTakerOfferIDs(counterTrades, pubKey):
  tradeTypes = ["order_book", "liquidity_pool", "v0"]
  syntheticTakerIDs = []
  for trades in counterTrades:
    for types in tradeTypes:
      contra = getattr(trades, types, 0)
      if(contra):
        contraID = contra.offer_id.int64
        break
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

