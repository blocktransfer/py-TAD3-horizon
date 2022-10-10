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
  cache = open(f"{G_DIR}/docs/caching-data/wash-sales.toml", "a")
  for offerIDs, adjustments in newOfferIDsMappedToChiefMemos.items():
    cache.write(f"{offerIDs} = \"{memos}\"\n")
  cache.close()

def getNewWashSalesFromStellar(queryAccount, cache):
  washSaleOfferIDsMappedToAdjustments = {}
  
  return washSaleOfferIDsMappedToAdjustments

