from globals import *

def getAssetAccountsRequestAddr(queryAsset):
  return f"{HORIZON_INST}/accounts?asset={queryAsset}:{BT_ISSUER}&{MAX_SEARCH}"

def getStellarBlockchainBalances(queryAsset):
  StellarBlockchainBalances = {}
  requestAddr = getAssetAccountsRequestAddr(queryAsset)
  ledger = requests.get(requestAddr).json()
  queryAsset = defGetAssetObjFromCode(queryAsset)
  while(ledger["_embedded"]["records"]):
    for accounts in ledger["_embedded"]["records"]:
      accountAddr = accounts["id"]
      for balances in accounts["balances"]:
        try:
          asset = Asset(balances["asset_code"], balances["asset_issuer"])
          if(asset == queryAsset):
            queryBalance = Decimal(balances["balance"])
            StellarBlockchainBalances[accountAddr] = queryBalance
            break
        except KeyError:
          continue
    ledger = getNextLedgerData(ledger)
  return StellarBlockchainBalances

def getNextLedgerData(ledger):
  nextAddr = ledger["_links"]["next"]["href"].replace("%3A", ":").replace("\u0026", "&")
  response = requests.get(nextAddr).json()
  try:
    if(response and not response["status"]):
      return getNextLedgerData(ledger)
  except KeyError:
    return response

def getStockOutstandingShares(queryAsset):
  requestAddr = f"{HORIZON_INST}/assets?asset_code={QueryAsset}&asset_issuer=BT_ISSUER"
  data = requests.get(requestAddr).json()
  outstandingInclTreasuryShares = data["_embedded"]["records"][0]["amount"]
  treasuryAddr = resolveFederationAddress(f"{queryAsset}*treasury.holdings")
  requestAddr = f"{HORIZON_INST}/accounts/{treasuryAddr}"
  accountBalances = requests.get(requestAddr).json()["balances"]
  queryAsset = defGetAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    asset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and asset == queryAsset):
      treasuryShares = balances["balance"]
      break
  return outstandingInclTreasuryShares - treasuryShares

def listAllIssuerAssets():
  allAssets = []
  requestAddress = f"{HORIZON_INST}/assets?asset_issuer={BT_ISSUER}&{MAX_SEARCH}"
  ledger = requests.get(requestAddress).json()
  while(ledger["_embedded"]["records"]):
    for entries in ledger["_embedded"]["records"]:
      allAssets.append(entries["asset_code"])
    ledger = getNextLedgerData(ledger)
  return allAssets

def defGetAssetObjFromCode(code):
  return Asset(code, BT_ISSUER)
