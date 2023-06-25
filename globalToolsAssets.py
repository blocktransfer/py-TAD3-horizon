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

def getNextLedgerData(links):
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
      print(f"Rate limited on ledger: {str(ledger)[:250]}")
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
  
  def getNumRestrictedShares(queryAsset):
  assetData = requestAssetRecords(queryAsset)
  explicitRestrictedShares = Decimal(assetData["claimable_balances_amount"])
  implicitRestrictedShares = Decimal("0")
  for classifiers, balances in assetData["balances"].items():  
    if(classifiers != "authorized"):
      implicitRestrictedShares += Decimal(balances)
  return explicitRestrictedShares + implicitRestrictedShares

# todo: Change diction to reflect use of Soroban for options compensation data
# def getNumAuthorizedSharesGeneratedButNotOutstanding(companyCode, queryAsset):
def getNumAuthorizedSharesNotIssued(companyCode, queryAsset):
  companyAccounts = [
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
  for accounts in companyAccounts:
    holdingAccountPublicKey = resolveFederationAddress(f"{companyCode}*{accounts}.holdings")
    shares += getCustodiedShares(queryAsset, holdingAccountPublicKey)
  return shares

def getCustodiedShares(queryAsset, account):
  if(not account): return 0
  accountBalances = getLedgerBalancesForPublicKey(publicKey)
  return getAssetBalanceFromAllBalances(queryAsset, accountBalances)

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

def getNumTreasuryShares(queryAsset):
  treasuryAddr = resolveFederationAddress(f"{queryAsset}*treasury.holdings")
  if(not treasuryAddr): return 0
  accountBalances = getLedgerBalancesForPublicKey(treasuryAddr)
  return getAssetBalanceFromAllBalances(queryAsset, accountBalances)

def getNumEmployeeBenefitShares(queryAsset):
  employeeBenefitAddr = resolveFederationAddress(f"{queryAsset}*reserved.employee.holdings")
  if(not employeeBenefitAddr): return 0
  accountBalances = getLedgerBalancesForPublicKey(employeeBenefitAddr)
  return getAssetBalanceFromAllBalances(queryAsset, accountBalances)

def getAssetBalanceFromAllBalances(queryAsset, accountBalances):
  asset = getAssetObjFromCode(queryAsset)
  for balances in accountBalances:
    if(balances["asset_type"] != "native"):
      searchAsset = Asset(balances["asset_code"], balances["asset_issuer"])
      if(searchAsset == asset):
        return balances["balance"]

def getLedgerBalancesForPublicKey(publicKey):
  url = f"{HORIZON_INST}/accounts/{publicKey}"
  return requestURL(url)["balances"]