from globals import *

def getValidAccountPublicKeys():
  validAccountPublicKeys = []
  with open(MICR_TXT) as MICR:
    next(MICR)
    for accounts in MICR:
      account = accounts.split("|")
      # Logic here to check account standing
      validAccountPublicKeys.append(account[0])
  return validAccountPublicKeys

def getAllPublicKeys():
  publicKeys = []
  with open(MICR_TXT) as MICR:
    next(MICR)
    for accounts in MICR:
      account = accounts.split("|")
      publicKeys.append(account[0])
  return publicKeys

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
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer="
  for addresses in BT_ISSUERS:
    if(requestRecords(url + addresses)):
      return addresses
  sys.exit(f"Could not find asset {queryAsset}")

def getAssetIssuerUntrustedTOML(queryAsset):
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer="
  for addresses in BT_ISSUERS:
    if(requestRecords(url + addresses)):
      return addresses
  sys.exit(f"Could not find asset {queryAsset}")

def requestAssetRecords(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={issuer}"
  return requestRecords(url)[0]

def requestAssetAccounts(queryAsset): # change this diction to chiefledger
  url = f"{HORIZON_INST}/accounts?{getURLendAsset(queryAsset)}" # TODO: change these these to use param get request jsons
  return requestURL(url)

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

def resolveFederationAddress(address):
  try:
    user, domain = address.split("*")
  except ValueError:
    return ""
  homeDomainFederationServer = getFederationServerFromDomain(domain)
  url = f"{homeDomainFederationServer}?q={address}&type=name"
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
def getAccountDataDict(address):
  url = f"{HORIZON_INST}/accounts/{address}"
  return requestURL(url)["data"]

def getAccountLinksDict(address):
  url = f"{HORIZON_INST}/accounts/{address}"
  return requestURL(url)["_links"]
### ###

def formatRawHref(href):
  return href.replace("{?cursor,limit,order}", f"?{MAX_SEARCH}")

def getPaymentsLedgerFromAccountLinks(accountLinks):
  return requestURL(
    formatRawHref(
      accountLinks["payments"]["href"]
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

def stripPagingNum(fullPaging):
  return fullPaging.split("-")[0]

