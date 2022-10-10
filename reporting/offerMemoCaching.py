import sys
sys.path.append("../")
from globals import *

def updateAllOfferIDs():
  cacheData = getOfferIDsMappedToChiefMemosFromCache()
  newOfferIDsMappedToChiefMemos = {}
  for addresses in getValidAccountPublicKeys():
    print(f"Querying new offers for {addresses}")
    newOfferIDsMappedToChiefMemos.update(
      getNewOfferIDsMappedToChiefMemosFromStellar(addresses, cacheData)
    )
  cache = open(f"{G_DIR}/docs/caching-data/offer-memos.toml", "a")
  for offerIDs, memos in newOfferIDsMappedToChiefMemos.items():
    cache.write(f"{offerIDs} = \"{memos}\"\n")
  cache.close()

def getNewOfferIDsMappedToChiefMemosFromStellar(queryAccount, cache):
  accountOfferIDsMappedToChiefMemos = {}
  requestAddr = f"{HORIZON_INST}/accounts/{queryAccount}/transactions?{MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for txns in ledger["_embedded"]["records"]:
      if(txns["source_account"] == queryAccount):
        resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
        for ops in resultXDR.result.results:
          op = ops.tr
          if(op.manage_buy_offer_result or op.manage_sell_offer_result):
            offerIDarr = []
            appendOfferIDsToArr(op, offerIDarr, queryAccount)
            for offerIDs in offerIDarr:
              localNew = offerIDs not in accountOfferIDsMappedToChiefMemos.keys()
              cacheNew = offerIDs not in cache.keys()
              if(offerIDs and localNew and cacheNew):
                try:
                  instructions = txns["memo"]
                except KeyError:
                  instructions = ""
                except TypeError:
                  pprint(txns)
                memo = "|".join([instructions, queryAccount])
                accountOfferIDsMappedToChiefMemos[offerIDs] = memo
    ledger = getNextLedgerData(ledger)
  return accountOfferIDsMappedToChiefMemos

def getAttr(obj, attr):
  def subGetAttr(obj, attr):
    return getattr(obj, attr)
  return functools.reduce(subGetAttr, [obj] + attr.split("."))

def appendOfferIDsToArr(op, offerIDarr, address):
  makerIDattr = "success.offer.offer.offer_id.int64"
  takerIDattr = "success.offers_claimed"
  try:
    offerID = getAttr(op.manage_sell_offer_result, makerIDattr)
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

