from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder
from datetime import datetime
from decimal import Decimal
from pprint import pprint
import requests, json

BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"

HORIZON_INST = "horizon.stellar.org"
MAX_NUM_DECIMALS = "7"
MAX_SEARCH = "200"

FALLBACK_MIN_FEE = 100
MAX_NUM_TXN_OPS = 100

#testing: 
BT_ISSUER = "GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM"
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
        except:
          continue
      StellarBlockchainBalances[accountAddress] = accountBalance
    # Go to next cursor
    requestAddress = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddress).json()
    blockchainRecords = data["_embedded"]["records"]
  return StellarBlockchainBalances

