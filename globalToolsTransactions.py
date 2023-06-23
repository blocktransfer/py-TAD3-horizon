from globals import *

def isFiat(queryAsset):
  return queryAsset == BT_DOLLAR or queryAsset == USDC_ASSET

def appendTransactionEnvelopeToArrayWithSourceAccount(transactionsArray, sourceAccount):
  transactionsArray.append(
    TransactionBuilder(
      source_account = sourceAccount,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )

def prepTxn(transaction, memo, signer):
  transaction = (
    transaction
    .add_text_memo(memo)
    .set_timeout(DEF_TXN_TIMEOUT)
    .build()
  )
  transaction.sign(signer)
  return transaction

def toFullAddress(street, streetExtra, city, state, postal, country):
  uncheckedArr = [street, streetExtra, city, state, postal, country]
  cleanArr = []
  for items in uncheckedArr:
    if(items):
      cleanArr.append(items)
  return ", ".join(cleanArr)

async def submitTxnAndWait(transaction):
  async with ServerAsync(
    horizon_url = HORIZON_INST,
    client = AiohttpClient()
  ) as server:
    return await server.submit_transaction(transaction)

def submitTxnGuaranteed(transaction):
  return redundant(transaction, 0)

def redundant(transaction, attempt):
  if(attempt > MAX_SUBMISSION_ATTEMPTS):
    return submitTxnStd(transaction)
  response, success = submitTxnStd(transaction)
  if(success):
    return response
  else:
    return redundant(transaction, attempt + 1)

def submitTxnStd(transaction):
  try:
    return server.submit_transaction(transaction), 1
  except (BadRequestError, BadResponseError) as err:
    return f"Tx submission failed: {err}", 0

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
  return int((day - unix_base).total_seconds())

def dayFromEpoch(epoch):
  try:
    return datetime.utcfromtimestamp(epoch)
  except ValueError:
    return "Epoch out of range"

