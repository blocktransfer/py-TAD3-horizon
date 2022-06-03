from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder, TrustLineFlags
from datetime import datetime
from decimal import Decimal
from pprint import pprint
import requests, json

# Debug issuers:
# accounts - GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM
# trustlines - GD7HBNPUAIK5QW7MLC7VKKHIQZCYZYCAC4YNRT3YOPYPQRK3G5ZGQJOS
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
BT_TREASURY = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
SECRET = "SBTPLXTXJDMJOXFPYU2ANLZI2ARDPHFKPKK4MJFYVZVBLXYM5AIP3LPK"

HORIZON_INST = "horizon.stellar.org"
MAX_NUM_DECIMALS = "7"
MAX_SEARCH = "200"

FALLBACK_MIN_FEE = 100
MAX_NUM_TXN_OPS = 100
BASE_FEE_MULT = 2

KYC_CSV_INST = "" # todo: make a style for a master identity ledger... store on offline airgapps sys with weekly? updates and sole physical backup monthly? with secure custodians (split btwn with partial images? - registered mail encrypted drives?) and then wipe Persona ea. week? on a 2-mo delayed basis? 
# that might be a bit much, and we could probably just use an authenticated sftp channel or put in Storj? 

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

