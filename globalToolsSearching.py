from globals import *

def getAssetObjFromCode(code):
  return Asset(code, getAssetIssuer(code))

def getAssetIssuer(queryAsset):
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer="
  for addresses in BT_ISSUERS:
    if(requestRecords(url + addresses)):
      return addresses
  sys.exit(f"Could not find asset {queryAsset}")

def requestAssetRecords(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={issuer}"
  return requestRecords(url)[0]

def requestAssetAccounts(queryAsset):
  url = f"{HORIZON_INST}/accounts?{getURLendAsset(queryAsset)}"
  return requestURL(url)

def getURLendAsset(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return f"asset={queryAsset}:{issuer}&{MAX_SEARCH}"

def getIssuerAccObj(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return server.load_account(account_id = issuer)

def getNumRestrictedShares(queryAsset):
  assetData = requestAssetRecords(queryAsset)
  explicitRestrictedShares = Decimal(assetData["claimable_balances_amount"])
  implicitRestrictedShares = Decimal("0")
  for classifiers, balances in assetData["balances"].items():  
    if(classifiers != "authorized"):
      implicitRestrictedShares += Decimal(balances)
  return explicitRestrictedShares + implicitRestrictedShares

def SHA3(input):
  return sha3_256(input.encode()).hexdigest()

def loadTomlData(link):
  return toml.loads(requests.get(link).content.decode())

def getFederationServerFromDomain(federationDomain):
  try:
    requestAddr = f"https://{federationDomain}/.well-known/stellar.toml"
    data = loadTomlData(requestAddr)
    return data["FEDERATION_SERVER"]
  except requests.exceptions.ConnectionError:
    return ""

def resolveFederationAddress(federationAddress):
  federationDomain = federationAddress.split("*")[1]
  homeDomainFederationServer = getFederationServerFromDomain(federationDomain)
  url = f"{homeDomainFederationServer}?q={federationAddress}&type=name"
  try:
    return requestURL(url)["account_id"]
  except requests.exceptions.MissingSchema:
    return ""

# todo: Change diction to reflect use of Soroban for options compensation data
def getNumAuthorizedSharesNotIssued(companyCode, queryAsset): # todo: Change this diction to reserved shares?
  issuerAccounts = [ # todo: Change this diction to companyAccounts?
    "authorized.DSPP",
    "initial.offering",
    "reg.a.offering",
    "reg.cf.offering",
    "reg.d.offering",
    "shelf.offering",
    "reserved.employee", # todo: stock options via Soroban -> these held in contract
    "treasury"
  ]
  shares = Decimal("0")
  for accounts in issuerAccounts:
    requestAccount = resolveFederationAddress(f"{companyCode}*{accounts}.holdings")
    shares += getCustodiedShares(queryAsset, requestAccount)
  return shares

def getCustodiedShares(queryAsset, account):
  if(not account): return 0
  url = f"{HORIZON_INST}/accounts/{account}"
  accountBalances = requestURL(url)["balances"]
  asset = getAssetObjFromCode(queryAsset)
  ### todo: Globalize this? ###
  for balances in accountBalances:
    searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and searchAsset == asset):
      return balances["balance"]
  ######

def getAffiliateShares(queryAsset): # TODO: rm, outdated
  companyCode = getCompanyCodeFromAssetCode(queryAsset)
  public = isPublic(companyCode)
  if(not public):
    affiliateAccount = requestAccount = resolveFederationAddress(f"{companyCode}*private.affiliate.holdings")
    return getCustodiedShares(queryAsset, affiliateAccount)
  else:
    affiliateBalances = Decimal("0")
    # fetch list of affiliates from accounts.toml
    # get their balances
    accounts = loadTomlData(BT_ACCOUNTS_TOML)
    pprint(accounts)
    return affiliateBalances

def getCompanyCodeFromAssetCode(queryAsset):
  for assets in loadTomlData(BT_STELLAR_TOML)["CURRENCIES"]:
    if(assets["code"] == queryAsset):
      issuerInfo = assets["attestation_of_reserve"]
      return loadTomlData(issuerInfo)["ISSUER"]["bt_company_code"]
  return 0

def isPublic(companyCode):
  issuerInfo = f"https://blocktransfer.io/assets/{companyCode}.toml"
  return loadTomlData(issuerInfo)["ISSUER"]["reporting_company"]

def getNumTreasuryShares(queryAsset):
  treasuryAddr = resolveFederationAddress(f"{queryAsset}*treasury.holdings")
  if(not treasuryAddr): return 0
  url = f"{HORIZON_INST}/accounts/{treasuryAddr}"
  accountBalances = requestURL(url)["balances"]
  asset = getAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and searchAsset == asset):
      return balances["balance"]

def getNumEmployeeBenefitShares(queryAsset):
  employeeBenefitAddr = resolveFederationAddress(f"{queryAsset}*reserved.employee.holdings")
  if(not employeeBenefitAddr): return 0
  url = f"{HORIZON_INST}/accounts/{employeeBenefitAddr}"
  accountBalances = requestURL(url)["balances"]
  asset = getAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and searchAsset == asset):
      return balances["balance"]

def getAssetCodeFromTomlLink(link):
  rawCode = link.split("/")[-1]
  return rawCode[:-5]

def getAccountDataDict(address):
  url = f"{HORIZON_INST}/accounts/{address}"
  return requestURL(url)["data"]

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
  return ITIN[2:-1]

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
      sys.exit("Bad validity: Searching/offer-memos")
    offerIDsMappedToChiefMemos[offerID] = memos
  return offerIDsMappedToChiefMemos

def getWashSaleOfferIDsMappedToAdjustments():
  washSaleOfferIDsMappedToAdjustments = {}
  cache = loadTomlData(WASH_SALE_TOML)
  for offerIDs, adjustments in cache.items():
    washSaleOfferIDsMappedToAdjustments[offerIDs] = adjustments
  return washSaleOfferIDsMappedToAdjustments

def getMemoFromTransaction(txn):
  try:
    return txn["memo"]
  except KeyError:
    return ""

def getCBmemoFromClaimableID(ID):
  CBcreationTxn = getCBcreationTxnFromClaimableID(ID)
  return getMemoFromTransaction(CBcreationTxn)

def getCBcreationTxnFromClaimableID(ID):
  url = f"{HORIZON_INST}/claimable_balances/{ID}/transactions"
  return requestRecords(url)[0]

def getClaimedIDfromClaimingTxnHashForAsset(transaction, queryAsset):
  url = f"{HORIZON_INST}/transactions/{transaction}/operations?limit={MAX_NUM_TXN_OPS}"
  userClaimTxnOps = requestRecords(url)
  for ops in userClaimTxnOps:
    try:
      originClaimableID = ops["balance_id"]
    except KeyError:
      continue
    claimingOpEffectsURL = ops["_links"]["effects"]["href"]
    for effects in requestRecords(claimingOpEffectsURL):
      try:
        if(effects["asset"].split(":")[0] == queryAsset):
          return originClaimableID
      except KeyError:
        continue

