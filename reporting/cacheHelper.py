import sys
sys.path.append("../")
from globals import *

def getOfferIDsMappedToChiefMemosFromCache():
  return readLatestCache("offer-memos")

def readLatestCache(type):
  path, height = getLatestCachePathAndBlockHeight(type)
  with open(path) as cache:
    return json.load(cache)

def archiveLatestCache(type="offer-memos"):
  path, height = getLatestCachePathAndBlockHeight(type)
  archivePath = f"{OUT_DIR}/oldCaches/{type}-{height}.json"
  shutil.move(path, archivePath)

def getLatestCachePathAndBlockHeight(type):
  highestLedgerNum = 0
  for files in os.listdir(CACHE_DIR):
    if(files.startswith(type)):
      ledgerNum = int(files.split("-")[-1].split(".")[0])
      if(ledgerNum > highestLedgerNum):
        latestCache = files
        highestLedgerNum = ledgerNum
  path = f"{CACHE_DIR}/{latestCache}"
  return path, highestLedgerNum


