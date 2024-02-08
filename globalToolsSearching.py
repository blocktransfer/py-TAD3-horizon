from globals import *

def getValidAccountPublicKeys():
  return requestAWS("accounts/public-keys/valid")

def getAllPublicKeys():
  return requestAWS("accounts/public-keys/all")

def fetchAccount(pubKey):
  return requestAWS(f"PII/{pubKey}")

def getAccountIDfromPubKey(PK):
  return fetchAccount(pubKey)["ID"]

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
  params = {
    "asset_code": queryAsset,
    "asset_issuer": getAssetIssuer(queryAsset)
  }
  return requestRecords("assets", params)[0]

def requestAssetAccounts(queryAsset): # change this diction to chiefledger
  path = f"accounts?{getURLendAsset(queryAsset)}"
  return requestXLM(path)

def getURLendAsset(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return f"asset={queryAsset}:{issuer}&{MAX_SEARCH}"

def getIssuerAccObj(queryAsset):
  issuer = getAssetIssuer(queryAsset)
  return server.load_account(account_id = issuer)

def getCompanyCodeFromAssetCode(queryAsset): # todo: Change this to use permanant diction
  for assets in getAllBTcompanies():
    try:
      code = assets["code_template"].split("?")[0]
    except KeyError:
      code = assets["code"]
    codeLength = len(code)
    if(code == queryAsset[:codeLength]):
      issuerInfo = assets["attestation_of_reserve"]
      return loadTomlData(issuerInfo)["ISSUER"]["bt_company_code"]
  return 0

def loadTomlData(link): # todo: Change this to use permanant diction
  return toml.loads(requests.get(link).content.decode())

def getAllBTcompanies():
  return xlm.sep.fetch_stellar_toml_async("blocktransfer.com")

# depricated, to be deleted by October
  # def getFederationServerFromDomain(federationDomain):
  #   try:
  #     url = f"https://{federationDomain}/.well-known/stellar.toml"
  #     data = loadTomlData(url)
  #     return data["FEDERATION_SERVER"]
  #   except requests.exceptions.ConnectionError:
  #     return ""

def resolveFederationAddress(addr):
  return xlm.resolve_stellar_address(addr)
  # depricated, to be deleted by October
    # try:
    #   user, domain = addr.split("*")
    # except ValueError:
    #   return ""
    # homeDomainFederationServer = getFederationServerFromDomain(domain)
    # url = f"{homeDomainFederationServer}?q={addr}&type=name"
    # try:
    #   return requestURL(url)["account_id"]
    # except KeyError:
    #   return ""

def isPublic(CIK):
  issuerInfo = f"https://blocktransfer.com/assets/{CIK}.toml"
  return loadTomlData(issuerInfo)["ISSUER"]["reporting_company"]

def getCIKfromTomlLink(link):
  rawCode = link.split("/")[-1]
  return rawCode[:-5]

def getCIKfromQueryAsset(code):
  match = re.search(r"\d+", code)
  return int(match.group()) if match else 0

def getLedgerDataForPK(pubKey):
  return requestXLM(f"accounts/{pubKey}")["data"]

def getAccountLinksDict(addr):
  return requestXLM(f"accounts/{addr}")["_links"]

def getPaymentsLedgerFromAccountLinks(accountLinks):
  return requestURL(
    accountLinks["payments"]["href"].replace(
      "{?cursor,limit,order}", "?limit=200"
    )
  )

def getISIN(queryAsset):
  try:
    for currencies in getAllBTcompanies():
      # match code_template startsWith
      
      
      # get full data loadTomlData(currencies["attestation_of_reserve"])
      
      
      # iterate through ["securities?"] // S&B
      for securities in []:
        if(securities["code"] == queryAsset):
          return securities["ISIN"]
  except KeyError:
    sys.exit(f"ITIN toml resolution failed")
  return 0

def getCUSIP(queryAsset):
  return getISIN[2:-1]

# THIS DOES NOT WORK #
def isCUSIP(query):
  allAssets = listAllIssuerAssets()
  allCUSIPs = []
  for assets in allAssets:
    allCUSIPs.append(getCUSIP(query))
  return query in allCUSIPs

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

def getCBsForPK(pubKey):
  allCBs = {}
  # Assume under 200 or do pagination links/records
  response = server.claimable_balances().for_claimant(pubKey).limit(200).call()
  for CBs in response["_embedded"]["records"]:
    CB = {}
    code, issuer = CBs["asset"].split(":")
    if issuer != BT_ISSUERS[0]: continue
    CB["asset"] = code
    CB["amount"] = CBs["amount"]
    otherClaimants = []
    for claimants in CBs["claimants"]:
      recipient = claimants["destination"]
      if recipient == pubKey:
        CB["claimable"] = claimants.get("predicate", {}).get("not", {}).get("abs_before", "available")
      else:
        otherClaimants.append(recipient)
    if otherClaimants:
      CB["otherClaimants"] = otherClaimants    
    allCBs[CBs["id"]] = CB
  return allCBs

