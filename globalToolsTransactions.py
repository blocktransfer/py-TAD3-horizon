from globals import *

def isFiat(queryAsset):
  return queryAsset == BT_DOLLARS or queryAsset == USDC_ASSET

# todo: pulling info twice here
def getValidAccountPublicKeys():
  validAccountPublicKeys = []
  MICR = open(MICR_TXT)
  next(MICR)
  for accounts in MICR:
    account = accounts.split("|")
    validAccountPublicKeys.append(account[0])
  MICR.close
  return validAccountPublicKeys

def appendTransactionEnvelopeToArrayWithSourceAccount(transactionsArray, sourceAccount):
  transactionsArray.append(
    TransactionBuilder(
      source_account = sourceAccount,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )

def toFullAddress(street, streetExtra, city, state, postal, country):
  uncheckedArr = [street, streetExtra, city, state, postal, country]
  cleanArr = []
  for items in uncheckedArr:
    if(items):
      cleanArr.append(items)
  return ", ".join(cleanArr)

#todo: stress test
def submitTxnGarunteed(transaction):
  while(True):
    if(server.submit_transaction(transaction)):
      return 1

def adjustNumSharesForStockSplits(numShares, purchaseTimestamp, queryAsset):
  splitsDict = {}
  data = loadTomlData(BT_STELLAR_TOML)
  for currencies in data["CURRENCIES"]:
    assetCode = getAssetCodeFromTomlLink(currencies["toml"])
    if(assetCode == queryAsset):
      data = loadTomlData(currencies["toml"])
      splitData = data["CURRENCIES"][0]["splits"].split("|")
      for splits in splitData:
        date = pandas.to_datetime(f"{splits.split('effective ')[1]}T00:00:00Z")
        splits = splits.split(" ")
        num = Decimal(splits[0])
        denom = Decimal(splits[2])
        splitsDict[date] = num / denom
      return splitsDict
  for splitTimestamps, splitRatios in splitsDict.items():
    if(purchaseTimestamp < splitTimestamps):
      numShares = numShares * splitRatios
  return numShares

def epochFromDay(day):
  return int((day - UNIX).total_seconds())

def dayFromEpoch(epoch):
  return datetime.datetime.utcfromtimestamp(epoch)

