from globals import *

def getLedgerBalances(queryAsset):
  ledgerBalances = {}
  ledger = requestAssetAccounts(queryAsset)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  queryAsset = getAssetObjFromCode(queryAsset)
  ### unrestricted shares only ###
  i = 0
  while(records):
    for accounts in records:
      for balances in accounts["balances"]:
        try:
          asset = Asset(balances["asset_code"], balances["asset_issuer"])
          if(asset == queryAsset):
            account = accounts["id"]
            balance = Decimal(balances["balance"])
            ledgerBalances[account] = balance
            break
        except KeyError:
          continue
    links, records = getNextLedgerData(links)
  return ledgerBalances

def getNextLedgerData(links): # depricated for async
  nextData = requests.get(
    links["next"]["href"]
    .replace("\u0026", "&")
    .replace("%3A", ":")
  ).json()
  try:
    checkForRateLimitFromLedgerData(nextData)
    return getLinksAndRecordsFromParsedLedger(nextData)
  except RateLimited:
    return getNextLedgerData(links)

def checkForRateLimitFromLedgerData(ledger):
  try:
    if(ledger and not ledger["status"]):
      raise RateLimited
  except KeyError:
    pass

def listAllIssuerAssets():
  allAssets = []
  for addresses in BT_ISSUERS:
    url = f"{HORIZON_INST}/assets?asset_issuer={addresses}&{MAX_SEARCH}"
    ledger = requestURL(url)
    links, records = getLinksAndRecordsFromParsedLedger(ledger)
    while(records):
      for entries in records:
        allAssets.append(entries["asset_code"])
      links, records = getNextLedgerData(links)
  return allAssets
  
  