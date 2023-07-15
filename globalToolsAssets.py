from globals import *

### HOW LEDGER SHARE BALANCES WORK ###

# Authorized shares on the ledger represent unrestricted stock when held outside of company accounts.
# Authorized_to_maintain_liabilities is used when an account is frozen due to government requirements.
#   These shouldn't meaningfully affect float, and are currently marked as unrestricted/outstanding.
# Unauthorized shares are unrestricted stock held by a company insider who can't trade without help.

# Claimable balances are restricted shares.
# The claimable date indicates when the shares become unrestricted, typically following SEC Rule 144.
# The release date may be denoted by a memo in other scenarios dictated by offline case-by-case terms.

# Employee stock grants, options, and similar arrangements are through Soroban.


### unrestricted shares only ###
def getLedgerBalances(queryAsset):
  ledgerBalances = {}
  ledger = requestAssetAccounts(queryAsset)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  queryAsset = getAssetObjFromCode(queryAsset)
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

### todo ###
def getLedgerBalancesV2(queryAsset):
  ledgerBalances = {}
  ledger = requestAssetAccounts(queryAsset)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  queryAsset = getAssetObjFromCode(queryAsset)
  i = 0
  while(records):
    for accounts in records:
      for balances in accounts["balances"]:
        try:
          asset = Asset(balances["asset_code"], balances["asset_issuer"])
          if(asset == queryAsset):
            account = accounts["id"]
            balance = {}
            balance["unrestricted"] = Decimal(balances["balance"])
            
            # CB lookup
            restricted = 1
            if(restricted):
              restricted
              balance["restricted"] = restricted
            
            ledgerBalances[account] = balance
            break
        except KeyError:
          continue
    links, records = getNextLedgerData(links)
  return ledgerBalances
######

def getNextLedgerData(links):
  nextData = requestURL(
    links["next"]["href"]
    .replace("\u0026", "&")
    .replace("%3A", ":")
  )
  try:
    checkForRateLimitFromLedgerData(nextData)
    return getLinksAndRecordsFromParsedLedger(nextData)
  except KeyError:
    print("KeyError in NextLedget function")
    pprint(links)
    print("->")
    pprint(nextData)
    return getNextLedgerData(links)

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

def getTransactionsForAsset(queryAsset):
  # When SE payments relaunched: 
    # Get all transfers
      # SEapiResponse = trySEpaymentsAPI
    # Get all trades
      # HorizonTradesSearch via horizon/trades?base_asset=DEMO...
  
  # tmp: search investor txns for payments
  
  # You need to iterate over all public keys to account for investors
  # that previously transacted with the queryAsset but don't own now.
  
  # use queryAsset DEMO to test transferSearching: 
  transactionsForAssets = {}
  allPublicKeys = debugGetAllCurrPublicKeysForAsset(queryAsset)
  for addresses in allPublicKeys:
    accountLinks = getAccountLinksDict(addresses)
    paymentsLedger = getPaymentsLedgerFromAccountLinks(accountLinks)
    paymentLinks, paymentRecords = getLinksAndRecordsFromParsedLedger(paymentsLedger)
    while(paymentRecords):
      for payments in paymentRecords:
        if(
          payments["type"] == "payment" and
          payments["asset_type"] != "native" and
          payments["asset_issuer"] in BT_ISSUERS and
          payments["asset_code"] == queryAsset
        ):
          transactionsForAssets[payments["paging_token"].split("-")[0]] = {
            "type": "transfer",
            "txHash": payments["transaction_hash"],
            "amount": Decimal(payments["amount"]),
            "from": payments["from"],
            "to": payments["to"],
            "timestamp": payments["created_at"],
          }
      paymentLinks, paymentRecords = getNextLedgerData(paymentLinks)
  
  # use queryAsset ETH to test tradeSearching:
  fiatAsset = USDC_ASSET # BT_DOLLAR
  url = f"{HORIZON_INST}/trades?base_asset_type={'credit_alphanum12' if len(queryAsset) > 4 else 'credit_alphanum4'}&base_asset_code={queryAsset}&base_asset_issuer={getAssetIssuer(queryAsset)}&counter_asset_type={fiatAsset.type}&counter_asset_code={fiatAsset.code}&counter_asset_issuer={fiatAsset.issuer}&{MAX_SEARCH}"
  try:
    tradesLedger = requestURL(url)
    tradeLinks, tradeRecords = getLinksAndRecordsFromParsedLedger(tradesLedger)
  except KeyError:
    print(f"No trades found for {queryAsset} against {fiatAsset.code}")
    return transactionsForAssets
  while(tradeRecords):
    for trades in tradeRecords:
      if(trades["trade_type"] != "liquidity_pool"): # BT doesn't support liquidity pools or path payments yet
        transactionsForAssets[trades["paging_token"].split("-")[0]] = {
          "type": "trade",
          "operationID": trades["id"].split("-")[0],
          "buyer": trades["counter_account"],
          "dollars": Decimal(trades["counter_amount"]),
          "seller": trades["base_account"],
          "shares": Decimal(trades["base_amount"]),
          "price": Decimal(trades["price"]["n"]) / Decimal(trades["price"]["d"]), # todo: globalize
          "timestamp": trades["ledger_close_time"]
        }
    tradeLinks, tradeRecords = getNextLedgerData(tradeLinks)
  return transactionsForAssets

