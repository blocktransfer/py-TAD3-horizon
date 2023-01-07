import sys
sys.path.append("../")
from globals import *

def updateAllOfferIDs():
  cacheData = getOfferIDsMappedToChiefMemosFromCache()
  newWashSaleOfferIDsMappedToAdjustments = {}
  for addresses in getValidAccountPublicKeys():
    print(f"Querying new wash sales for {addresses}")
    newWashSaleOfferIDsMappedToAdjustments.update(
      getNewWashSalesFromStellar(addresses, cacheData)
    )
  with open(f"{G_DIR}/docs/.well-known/wash-sales.toml", "a") as cache:
    for offerIDs, adjustments in newOfferIDsMappedToChiefMemos.items():
      cache.write(f"{offerIDs} = \"{memos}\"\n")

def getNewWashSalesFromStellar(queryAccount, cache):
  washSaleOfferIDsMappedToAdjustments = {}
  # this does not properly check via dynamo query yet (cache?)
  return washSaleOfferIDsMappedToAdjustments

