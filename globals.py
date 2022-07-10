from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder, TrustLineFlags
from datetime import datetime
from decimal import Decimal
from pprint import pprint
import os.path, requests, json, toml
G_DIR = os.path.dirname(__file__)

# Debug issuers:
# accounts - GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM
# trustlines - GD7HBNPUAIK5QW7MLC7VKKHIQZCYZYCAC4YNRT3YOPYPQRK3G5ZGQJOS
BT_ISSUER = "GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
BT_TREASURY = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
SECRET = "SBTPLXTXJDMJOXFPYU2ANLZI2ARDPHFKPKK4MJFYVZVBLXYM5AIP3LPK"
MICR_CSV = G_DIR + "/../../pii/master-identity-catalog-records.csv"

HORIZON_INST = "horizon.stellar.org"
MAX_NUM_DECIMALS = "7"
MAX_SEARCH = "200"
MAX_NUM_TXN_OPS = 100
BASE_FEE_MULT = 2

server = Server(horizon_url= "https://" + HORIZON_INST)
issuer = server.load_account(account_id = BT_ISSUER)
distributor = server.load_account(account_id = BT_DISTRIBUTOR)
treasury = server.load_account(account_id = BT_TREASURY)
fee = server.fetch_base_fee()*BASE_FEE_MULT

def getStellarBlockchainBalances(queryAsset):
  StellarBlockchainBalances = {}
  requestAddress = "https://" + HORIZON_INST + "/accounts?asset=" + queryAsset + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
  data = requests.get(requestAddress).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for accounts in blockchainRecords:
      accountAddress = accounts["id"]
      for balances in accounts["balances"]:
        try:
          if balances["asset_code"] == queryAsset and balances["asset_issuer"] == BT_ISSUER:
            accountBalance = Decimal(balances["balance"])
        except Exception:
          continue
      StellarBlockchainBalances[accountAddress] = accountBalance
    # Go to next cursor
    requestAddress = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddress).json()
    blockchainRecords = data["_embedded"]["records"]
  return StellarBlockchainBalances

#todo: test
def submitTxnGarunteed(transaction):
  while(True):
    if(server.submit_transaction(transaction)):
      return 1

def appendTransactionEnvelopeToArrayWithSourceAccount(transactionsArray, sourceAccount):
  transactionsArray.append(
    TransactionBuilder(
      source_account = sourceAccount,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )

def resolveFederationAddress(properlyFormattedAddr):
  splitAddr = properlyFormattedAddr.split("*")
  federationName = splitAddr[0]
  federationDomain = splitAddr[1]
  homeDomainFederationServer = getFederationServerFromDomain(federationDomain)
  requestAddr = homeDomainFederationServer + "?q=" + properlyFormattedAddr + "&type=name"
  data = requests.get(requestAddr).json()
  try: 
    return data["account_id"]
  except Exception:
    sys.exit("Could not find {}".format(properlyFormattedAddr))

def getFederationServerFromDomain(federationDomain):
  try:
    requestAddr = "https://" + federationDomain + "/.well-known/stellar.toml"
    data = toml.loads(requests.get(requestAddr).content.decode())
    homeDomainFederationServer = data["FEDERATION_SERVER"]
  except Exception:
    sys.exit("Failed to lookup federation server at {}".format(federationDomain))
  return homeDomainFederationServer if homeDomainFederationServer.split("/")[-1] else homeDomainFederationServer[:-1]

def toFullAddress(street, streetExtra, city, state, postal, country):
  uncheckedArr = [street, streetExtra, city, state, postal, country]
  cleanArr = []
  for items in uncheckedArr:
    if(items):
      cleanArr.append(items)
  return ". ".join(cleanArr)

