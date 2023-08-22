import sys
sys.path.append("../")
from globals import *

import shutil

def getOfferIDsMappedToChiefMemosFromCache():
  return readCache("offer-memos")

def readCache(type):
  path, height = getCachePathAndBlockHeight(type)
  with open(path) as cache:
    return height, json.load(cache)

def archiveCache(type):
  path, height = getCachePathAndBlockHeight(type)
  archivePath = f"{OUT_DIR}/oldCaches/{type}-{height}.json"
  shutil.move(path, archivePath)

def saveCache(cache, type, height):
  path = f"{CACHE_DIR}/{type}-{height}.json"
  with open(path, "w") as cacheFile:
    json.dump(cache, cacheFile)

def getCachePathAndBlockHeight(type):
  for files in os.listdir(CACHE_DIR):
    if(files.startswith(type)):
      path = f"{CACHE_DIR}/{files}"
      height = int(
        files
        .split("-")[-1]
        .split(".")[0]
      )
      return path, height

