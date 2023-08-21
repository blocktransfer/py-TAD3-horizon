import sys
sys.path.append("../")
from globals import *

cache = getOfferIDsMappedToChiefMemosFromCache()

def updateCache():
  block = getRefBlock()
  for pubKeys in getValidAccountPublicKeys():
    print(f"Querying new offers for {pubKeys}")
    updateSuccessfulOfferIDsMappedToChiefMemosCacheForPK(pubKeys)
  saveCache("offer-memos", block)

def updateSuccessfulOfferIDsMappedToChiefMemosCacheForPK(pubKey):
  ledger = requestXLM(f"accounts/{pubKey}/transactions")
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for txns in records:
      if(txns["source_account"] == pubKey):
        resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
        for ops in resultXDR.result.results:
          op = ops.tr
          if(op.manage_buy_offer_result or op.manage_sell_offer_result):
            for offerIDs in getListOpOfferIDreturnsMultipleForMarketOrder(op, pubKey):
              if(offerIDs not in cache):
                cache[offerIDs] = getMemoFromTransaction(txns)
    links, records = getNextLedgerData(links)

def getAttr(obj, attr):
  def subGetAttr(obj, attr):
    return getattr(obj, attr)
  return functools.reduce(subGetAttr, [obj] + attr.split("."))

def getListOpOfferIDreturnsMultipleForMarketOrder(op, pubKey):
  makerIDattr = "success.offer.offer.offer_id.int64"
  try:
    return [getAttr(op.manage_sell_offer_result, makerIDattr)]
  except AttributeError:
    try:
      return [getAttr(op.manage_buy_offer_result, makerIDattr)]
    except AttributeError:
      takerIDattr = "success.offers_claimed"
      try:
        claimedOffersObj = getAttr(op.manage_sell_offer_result, takerIDattr)
      except AttributeError:
        claimedOffersObj = getAttr(op.manage_buy_offer_result, takerIDattr)
      IDattr = "offer_id.int64"
      offerIDsConsumed = []
      for trades in claimedOffersObj:
        try:
          contraID = getAttr(trades.order_book, IDattr)
        except AttributeError:
          try:
            contraID = getAttr(trades.liquidity_pool, IDattr)
          except AttributeError:
            contraID = getAttr(trades.v0, IDattr)
        offerIDsConsumed.append(
          getOfferIDfromContraID(contraID, pubKey)
        )
      return offerIDsConsumed

def getOfferIDfromContraID(offerID, pubKey):
  ledger = requestXLM(f"offers/{offerID}/trades")
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for trades in records:
      if(trades["counter_account"] == pubKey):
        return int(trades["counter_offer_id"])
      elif(trades["base_account"] == pubKey):
        return int(trades["base_offer_id"])
    links, records = getNextLedgerData(links)

def getListOpOfferIDreturnsMultipleForMarketOrderV2betaTestingReq(op, pubKey):
  if(op.manage_sell_offer_result):
    if(op.manage_sell_offer_result.success.offer):
      return op.manage_sell_offer_result.success.offer.offer.offer_id.int64
    else:
      claimedOffersObj = op.manage_sell_offer_result.success.offers_claimed
  else:
    if(op.manage_buy_offer_result.success.offer):
      return op.manage_buy_offer_result.success.offer.offer.offer_id.int64
    else:
      claimedOffersObj = op.manage_buy_offer_result.success.offers_claimed
  offerIDsConsumed = []
  for trades in claimedOffersObj:
    try:
      contraID = trades.order_book.offer_id.int64
    except AttributeError:
      try:
        contraID = trades.liquidity_pool.offer_id.int64
      except AttributeError:
        contraID = trades.v0.offer_id.int64
    offerIDsConsumed.append(
      getOfferIDfromContraID(contraID, pubKey)
    )
  return offerIDsConsumed


def saveCache(type, block):
  path = f"{CACHE_DIR}/{type}-{block}.json"
  with open(path, "w") as cacheFile:
    json.dump(cache, cacheFile)

addr = "GC5TUPFLOXCINDYHQVYYLLVYP6GKHT65ELB2Q2WLFTGN63YYIXPQTDFJ"
print(getPubKeyOfferIDsMappedToChiefMemosNotCached(addr))