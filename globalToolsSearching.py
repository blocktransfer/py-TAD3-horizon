from globals import *

def getNumRestrictedShares(queryAsset):
  assetAddr = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  assetData = requests.get(assetAddr).json()["_embedded"]["records"][0]
  explicitRestrictedShares = Decimal(assetData["claimable_balances_amount"])
  implicitRestrictedShares = Decimal("0")
  for classifiers, balances in assetData["balances"].items():  
    if(classifiers != "authorized"):
      implicitRestrictedShares += Decimal(balances)
  return explicitRestrictedShares + implicitRestrictedShares

def loadTomlData(link):
  return toml.loads(requests.get(link).content.decode())

def getFederationServerFromDomain(federationDomain):
  try:
    requestAddr = f"https://{federationDomain}/.well-known/stellar.toml"
    data = loadTomlData(requestAddr)
    return data["FEDERATION_SERVER"]
  except requests.exceptions.ConnectionError:
    return ""

def resolveFederationAddress(queryAddr):
  splitAddr = queryAddr.split("*")
  federationName = splitAddr[0]
  federationDomain = splitAddr[1]
  homeDomainFederationServer = getFederationServerFromDomain(federationDomain)
  requestAddr = f"{homeDomainFederationServer}?q={queryAddr}&type=name"
  try:
    return requests.get(requestAddr).json()["account_id"]
  except requests.exceptions.MissingSchema:
    return ""

def getNumTreasuryShares(queryAsset):
  treasuryAddr = resolveFederationAddress(f"{queryAsset}*treasury.holdings")
  if(not treasuryAddr): return 0
  requestAddr = f"{HORIZON_INST}/accounts/{treasuryAddr}"
  accountBalances = requests.get(requestAddr).json()["balances"]
  asset = getAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and searchAsset == asset):
      return balances["balance"]

def getNumEmployeeBenefitShares(queryAsset):
  employeeBenefitAddr = resolveFederationAddress(f"{queryAsset}*reserved.employee.holdings")
  if(not employeeBenefitAddr): return 0
  requestAddr = f"{HORIZON_INST}/accounts/{employeeBenefitAddr}"
  accountBalances = requests.get(requestAddr).json()["balances"]
  asset = getAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and searchAsset == asset):
      return balances["balance"]

def getAssetCodeFromTomlLink(link):
  rawCode = link.split("/")[-1]
  return rawCode[:-5]

def getAccountDataDict(address):
  requestAddr = f"{HORIZON_INST}/accounts/{address}"
  return requests.get(requestAddr).json()["data"]

def getITIN(ticker):
  try:
    data = loadTomlData(BT_STELLAR_TOML)
    for currencies in data["CURRENCIES"]:
      assetCode = getAssetCodeFromTomlLink(currencies["toml"])
      if(assetCode == ticker):
        return currencies["code"]
  except KeyError:
    sys.exit(f"ITIN toml resolution failed")
  return 0

def getCUSIP(ITIN):
  return ITIN[1:-1]

def isCUSIP(query):
  allAssets = listAllIssuerAssets()
  allCUSIPs = []
  for assets in allAssets:
    allCUSIPs.append(getCUSIP(query))
  return query in allCUSIPs

def getOfferIDsMappedToChiefMemosFromCache():
  offerIDsMappedToChiefMemos = {}
  cache = loadTomlData(OFFER_MEMO_TOML)
  for offerIDs, memos in cache.items():
    try:
      offerID = int(offerIDs)
    except ValueError:
      sys.exit("Critical data validity error")
    offerIDsMappedToChiefMemos[offerID] = memos
  return offerIDsMappedToChiefMemos

def getWashSaleOfferIDsMappedToAdjustments(combinedTradeData):
  washSaleOfferIDsMappedToAdjustments = {}
  cache = loadTomlData(WASH_SALES_TOML)
  for offerIDs, adjustments in cache.items():
    offerIDsMappedToChiefMemos[offerIDs] = adjustments
  return washSaleOfferIDsMappedToAdjustments

