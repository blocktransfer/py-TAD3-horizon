from globals import *

def isFiat(queryAsset):
  return queryAsset == USD_ASSET or queryAsset == USDC_ASSET

def getValidAccountPublicKeys():
  validAccountPublicKeys = []
  inFile = open(MICR_TXT)
  MICR_TXT = inFile.read().strip().split("\n")
  inFile.close()
  for lines in MICR[1:]:
    lines = lines.split(",")
    validAccountPublicKeys.append(lines[0]) # assumes only one account
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