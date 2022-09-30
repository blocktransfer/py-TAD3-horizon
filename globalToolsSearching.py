def getAssetAccountsRequestAddr(queryAsset):
  return f"https://{HORIZON_INST}/accounts?asset={queryAsset}:{BT_ISSUER}&limit={MAX_SEARCH}"

def getStellarBlockchainBalances(queryAsset):
  StellarBlockchainBalances = {}
  requestAddr = getAssetAccountsRequestAddr(queryAsset)
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for accounts in ledger["_embedded"]["records"]:
      accountAddr = accounts["id"]
      for balances in accounts["balances"]:
        try:
          if balances["asset_code"] == queryAsset and balances["asset_issuer"] == BT_ISSUER:
            queryBalance = Decimal(balances["balance"])
        except KeyError:
          continue
      StellarBlockchainBalances[accountAddr] = queryBalance
    ledger = getNextLedgerData(ledger)
  return StellarBlockchainBalances

def getNextLedgerData(ledger):
  nextAddr = ledger["_links"]["next"]["href"].replace("%3A", ":").replace("\u0026", "&")
  ledger = requests.get(nextAddr).json()
  return ledger

def resolveFederationAddress(properlyFormattedAddr):
  splitAddr = properlyFormattedAddr.split("*")
  federationName = splitAddr[0]
  federationDomain = splitAddr[1]
  homeDomainFederationServer = getFederationServerFromDomain(federationDomain)
  requestAddr = f"{homeDomainFederationServer}?q={properlyFormattedAddr}&type=name"
  data = requests.get(requestAddr).json()
  try: 
    return data["account_id"]
  except Exception:
    sys.exit("Could not find {}".format(properlyFormattedAddr))

def getFederationServerFromDomain(federationDomain):
  def formatNoEndSlash(link):
    return link if link.split("/")[-1] else link[:-1]
  try:
    requestAddr = f"https://{federationDomain}/.well-known/stellar.toml"
    data = loadTomlData(requestAddr)
    homeDomainFederationServer = formatNoEndSlash(data["FEDERATION_SERVER"])
  except Exception:
    sys.exit(f"Failed to lookup federation server at {federationDomain}")
  return homeDomainFederationServer

def loadTomlData(link):
  return toml.loads(requests.get(link).content.decode())

def getAssetCodeFromTomlLink(link):
  return link[32:-5]





