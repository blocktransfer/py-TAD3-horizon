from globals import *

def getValidAccountPublicKeys():
  return requestAWS("accounts/public-keys/valid")

def getAllPublicKeys():
  return requestAWS("accounts/public-keys/all")

def fetchAccount(pubKey):
  return requestAWS(f"PII/{pubKey}")

def debugGetAllCurrPublicKeysForAsset(queryAsset):
  currPublicKeys = []
  ledger = requestAssetAccounts(queryAsset)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  queryAsset = getAssetObjFromCode(queryAsset)
  while(records):
    for accounts in records:
      currPublicKeys.append(accounts["id"])
    links, records = getNextLedgerData(links)
  return currPublicKeys

def getAssetObjFromCode(code):
  return Asset(code, getAssetIssuer(code))

def getAssetIssuer(queryAsset):
  path = f"assets?asset_code={queryAsset}&asset_issuer="
  for addrs in BT_ISSUERS:
    if(requestRecords(path + addrs)):
      return addrs
  sys.exit(f"Could not find asset {queryAsset}")

def getAssetIssuerUntrustedTOML(queryAsset):
  path = f"assets?asset_code={queryAsset}&asset_issuer="
  for addrs in BT_ISSUERS:
    if(requestRecords(path + addrs)):
      return addrs
  sys.exit(f"Could not find asset {queryAsset}")

def requestAssetRecords(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  path = f"assets?asset_code={queryAsset}&asset_issuer={issuer}"
  return requestRecords(path)[0]

def requestAssetAccounts(queryAsset): # change this diction to chiefledger
  path = f"accounts?{getURLendAsset(queryAsset)}" # TODO: change these these to use param get request jsons
  return requestXLM(path)

def getURLendAsset(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return f"asset={queryAsset}:{issuer}&{MAX_SEARCH}"

def getIssuerAccObj(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return server.load_account(account_id = issuer)

def getCompanyCodeFromAssetCode(queryAsset):
  for assets in loadTomlData(BT_STELLAR_TOML)["CURRENCIES"]:
    try:
      code = assets["code_template"].split("?")[0]
    except KeyError:
      code = assets["code"]
    codeLength = len(code)
    if(code == queryAsset[:codeLength]):
      issuerInfo = assets["attestation_of_reserve"]
      return loadTomlData(issuerInfo)["ISSUER"]["bt_company_code"]
  return 0

def loadTomlData(link):
  return toml.loads(requests.get(link).content.decode())

def getFederationServerFromDomain(federationDomain):
  try:
    url = f"https://{federationDomain}/.well-known/stellar.toml"
    data = loadTomlData(url)
    return data["FEDERATION_SERVER"]
  except requests.exceptions.ConnectionError:
    return ""

def resolveFederationAddress(addr):
  try:
    user, domain = addr.split("*")
  except ValueError:
    return ""
  homeDomainFederationServer = getFederationServerFromDomain(domain)
  url = f"{homeDomainFederationServer}?q={addr}&type=name"
  try:
    return requestURL(url)["account_id"]
  except KeyError:
    return ""

def isPublic(companyCode):
  issuerInfo = f"https://blocktransfer.io/assets/{companyCode}.toml"
  return loadTomlData(issuerInfo)["ISSUER"]["reporting_company"]

def getAssetCodeFromTomlLink(link):
  rawCode = link.split("/")[-1]
  return rawCode[:-5]

### potentially combine, see todo items for URL request reformatting to use params ###
def getAccountDataDict(addr):
  path = f"accounts/{addr}"
  return requestXLM(path)["data"]

def getAccountLinksDict(addr):
  path = f"accounts/{addr}"
  return requestXLM(path)["_links"]
### ###

def getPaymentsLedgerFromAccountLinks(accountLinks):
  return requestURL(
    accountLinks["payments"]["href"].replace(
      "{?cursor,limit,order}", "?limit=200"
    )
  )

def getISIN(ticker):
  try:
    data = loadTomlData(BT_STELLAR_TOML)
    for currencies in data["CURRENCIES"]:
      assetCode = getAssetCodeFromTomlLink(currencies["toml"])
      if(assetCode == ticker):
        return currencies["code"]
  except KeyError:
    sys.exit(f"ITIN toml resolution failed")
  return 0

def getCUSIP(ISIN):
  return ISIN[2:-1]

def isCUSIP(query):
  allAssets = listAllIssuerAssets()
  allCUSIPs = []
  for assets in allAssets:
    allCUSIPs.append(getCUSIP(query))
  return query in allCUSIPs

def getOfferIDsMappedToChiefMemosFromCache():
  path = f"{CACHE_DIR}/offer-memos.json"
  with open(path) as cache:
    return json.load(cache)

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
  path = f"claimable_balances/{ID}/transactions"
  return requestRecords(path)[0]

def getClaimedIDfromClaimingTxnHashForAsset(transaction, queryAsset):
  path = f"transactions/{transaction}/operations"
  userClaimTxnOps = requestRecords(path)
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

def stripPagingNum(pagingTkn):
  return pagingTkn.split("-")[0]

def getRefBlock():
  return requestXLM("")["history_latest_ledger"] - HIST_SAFETY_REWIND_BLOCKS

