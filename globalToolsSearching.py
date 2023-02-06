from globals import *

def getAssetIssuer(queryAsset):
  requestAddr = getAssetAddress(queryAsset)
  for addresses in BT_ISSUERS:
    if(requests.get(requestAddr + addresses).json()["_embedded"]["records"]):
      return addresses
  sys.exit(f"Could not find asset {queryAsset}")

def getAssetAddress(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={issuer}"

def getAssetAccountsAddress(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return f"{HORIZON_INST}/accounts?asset={queryAsset}:{issuer}&{MAX_SEARCH}"

def getIssuerAccObj(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return server.load_account(account_id = issuer)

def getNumRestrictedShares(queryAsset):
  requestAddr = getAssetAddress(queryAsset)
  assetData = requests.get(requestAddr).json()["_embedded"]["records"][0]
  explicitRestrictedShares = Decimal(assetData["claimable_balances_amount"])
  implicitRestrictedShares = Decimal("0")
  pprint(assetData)
  for classifiers, balances in assetData["balances"].items():  
    if(classifiers != "authorized"):
      implicitRestrictedShares += Decimal(balances)
  return explicitRestrictedShares + implicitRestrictedShares

getNumRestrictedShares("DEMO")

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

def getNumAuthorizedSharesNotIssued(companyCode):
  issuerAccounts = [
    "authorized.DSPP",
    "initial.offering",
    "reg.a.offering",
    "reg.cf.offering",
    "reg.d.offering",
    "shelf.offering",
    "reserved.employee", # todo: stock options via Soroban
    "treasury"
  ]
  shares = Decimal("0")
  for accounts in issuerAccounts:
    requestAccount = resolveFederationAddress(f"{companyCode}*{accounts}.holdings")
    shares += getCustodiedShares(queryAsset, requestAccount)
  return shares

def getCustodiedShares(queryAsset, account):
  if(not account): return 0
  requestAddr = f"{HORIZON_INST}/accounts/{account}"
  accountBalances = requests.get(requestAddr).json()["balances"]
  asset = getAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
    if(balances["asset_type"] != "native" and searchAsset == asset):
      return balances["balance"]

def getAffiliateShares(queryAsset):
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
  requestAddr = f"{HORIZON_INST}/claimable_balances/{ID}/transactions"
  CBcreationTxn = requests.get(requestAddr).json()["_embedded"]["records"][0]
  return getMemoFromTransaction(CBcreationTxn)

def getCBmemoFromClaimingTransactionID(ID):
  requestAddr = f"{HORIZON_INST}/transactions/{ID}"
  transactionEnvXDR = requests.get(requestAddr).json()["envelope_xdr"]
  userClaimOp = TransactionEnvelope.from_xdr(transactionEnvXDR).v1.tx.operations[0] 
  # Assume user claims only one asset at a time, 
  # as reverse lookup from txn hash otherwise can mix up assets
  originalClaimableID = userClaimOp.body.claim_claimable_balance_op.balance_id.v0.hash.hex()
  return getCBmemoFromClaimableID(f"{'0' * 8}{originalClaimableID}")

