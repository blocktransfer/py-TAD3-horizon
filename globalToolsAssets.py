from globals import *

def getLedgerBalances(queryAsset):
  ledgerBalances = {}
  requestAddr = getAssetAccountsAddress(queryAsset)
  ledger = requests.get(requestAddr).json()
  queryAsset = getAssetObjFromCode(queryAsset)
  while(ledger["_embedded"]["records"]):
    for accounts in ledger["_embedded"]["records"]:
      account = accounts["id"]
      for balances in accounts["balances"]:
        try:
          asset = Asset(balances["asset_code"], balances["asset_issuer"])
          if(asset == queryAsset):
            balance = Decimal(balances["balance"])
            ledgerBalances[account] = balance
            break
        except KeyError:
          continue
    ledger = getNextLedgerData(ledger)
  return ledgerBalances

def getNextLedgerData(ledger):
  nextURL = (
    ledger["_links"]["next"]["href"]
    .replace("\u0026", "&")
    .replace("%3A", ":")
  )
  response = requests.get(nextURL).json()
  try: # Overcome rate limits
    if(response and not response["status"]):
      return getNextLedgerData(ledger)
  except KeyError:
    return response

def listAllIssuerAssets():
  allAssets = []
  for addresses in BT_ISSUERS:
    requestAddress = f"{HORIZON_INST}/assets?asset_issuer={addresses}&{MAX_SEARCH}"
    ledger = requests.get(requestAddress).json()
    while(ledger["_embedded"]["records"]):
      for entries in ledger["_embedded"]["records"]:
        allAssets.append(entries["asset_code"])
      ledger = getNextLedgerData(ledger)
  return allAssets

def getAssetObjFromCode(code):
  return Asset(code, getAssetIssuer(code))

