import sys
sys.path.append("../")
from globals import *

def updateAllOfferIDs():
  offerMemos = getOfferIDsMappedToChiefMemosFromCache()
  newOfferIDsMappedToChiefMemos = {}
  for pubKeys in getValidAccountPublicKeys():
    print(f"Querying new offers for {pubKeys}")
    newOfferIDsMappedToChiefMemos.update(
      getPubKeyOfferIDsMappedToChiefMemosNotCached(pubKeyes, offerMemos)
    )
  with open(f"{CACHE_DIR}/offer-memos.toml", "a") as cache:
    for offerIDs, memos in newOfferIDsMappedToChiefMemos.items():
      cache.write(f"{offerIDs} = \"{memos}\"\n")

def getPubKeyOfferIDsMappedToChiefMemosNotCached(pubKey, existingOfferMemos):
  pubKeyOfferIDsMappedToChiefMemos = {}
  path = f"accounts/{pubKey}/transactions?{MAX_SEARCH}"
  ledger = requestXLM(path)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for txns in records:
      if(txns["source_account"] == pubKey):
        resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
        for ops in resultXDR.result.results:
          op = ops.tr
          if(op.manage_buy_offer_result or op.manage_sell_offer_result):
            offerIDarr = []
            appendOfferIDsToArr(op, offerIDarr, pubKey)
            for offerIDs in offerIDarr:
              noSyntheticCollisions = offerIDs not in pubKeyOfferIDsMappedToChiefMemos.keys()
              newOfferMemos = offerIDs not in existingOfferMemos.keys()
              if(offerIDs and noSyntheticCollisions and newOfferMemos):
                instructions = getMemoFromTransaction(txns)
                except TypeError:
                  pprint(txns)
                memo = "|".join([instructions, pubKey])
                pubKeyOfferIDsMappedToChiefMemos[offerIDs] = memo
    links, records = getNextLedgerData(links)
  return pubKeyOfferIDsMappedToChiefMemos

def getAttr(obj, attr):
  def subGetAttr(obj, attr):
    return getattr(obj, attr)
  return functools.reduce(subGetAttr, [obj] + attr.split("."))

def appendOfferIDsToArr(op, offerIDarr, pubKey):
  makerIDattr = "success.offer.offer.offer_id.int64"
  takerIDattr = "success.offers_claimed"
  try:
    offerID = getAttr(op.manage_sell_offer_result, makerIDattr)
  except AttributeError:
    try:
      offerID = getAttr(op.manage_buy_offer_result, makerIDattr)
    except AttributeError:
      try:
        offerID = resolveTakerOffer(getAttr(op.manage_sell_offer_result, takerIDattr), offerIDarr, pubKey)
      except AttributeError:
        offerID = resolveTakerOffer(getAttr(op.manage_buy_offer_result, takerIDattr), offerIDarr, pubKey)
  return offerIDarr.append(offerID)

def resolveTakerOffer(offersClaimed, offerIDarr, pubKey):
  IDattr = "offer_id.int64"
  offerID = 0
  for trades in offersClaimed:
    try:
      offerID = getOfferIDfromContraID(getAttr(trades.order_book, IDattr), pubKey)
    except AttributeError:
      try:
        offerID = getOfferIDfromContraID(getAttr(trades.liquidity_pool, IDattr), pubKey)
      except AttributeError:
        offerID = getOfferIDfromContraID(getAttr(trades.v0, IDattr), pubKey)
    offerIDarr.append(offerID)
  return offerID

def getOfferIDfromContraID(offerID, pubKey):
  ledger = requestURL(f"{HORIZON_INST}/offers/{offerID}/trades?{MAX_SEARCH}")
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for trades in records:
      if(trades["counter_account"] == pubKey):
        return int(trades["counter_offer_id"])
      elif(trades["base_account"] == pubKey):
        return int(trades["base_offer_id"])
    links, records = getNextLedgerData(links)

