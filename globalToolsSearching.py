import globals

def loadTomlData(link):
  return toml.loads(requests.get(link).content.decode())

def getAssetCodeFromTomlLink(link):
  return link[32:-5]

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

def getCUSIP(queryAsset):
  try:
    data = loadTomlData(BT_STELLAR_TOML)
    for currencies in data["CURRENCIES"]:
      assetCode = getAssetCodeFromTomlLink(currencies["toml"])
      if(assetCode == queryAsset):
        data = loadTomlData(currencies["toml"])
        CUSIP = currencies["anchor_asset"]
        break
  except Exception:
    sys.exit(f"Failed to lookup ITIN for {queryAsset}")
  return CUSIP



