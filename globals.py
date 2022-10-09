from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder, TrustLineFlags
from stellar_sdk.xdr import TransactionResult
from datetime import datetime
from decimal import Decimal
from pprint import pprint
import json, os.path, pandas, requests, sys, toml

G_DIR = os.path.dirname(__file__)
sys.path.append("../")
try:
  from local_secrets import *
except ModuleNotFoundError:
  TRIAL_KEY = "SBTPLXTXJDMJOXFPYU2ANLZI2ARDPHFKPKK4MJFYVZVBLXYM5AIP3LPK"
  ISSUER_KEY = DISTRIBUTOR_KEY = TREASURY_KEY = TRIAL_KEY

# Debug issuers:
# accounts - GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM
# trustlines - GD7HBNPUAIK5QW7MLC7VKKHIQZCYZYCAC4YNRT3YOPYPQRK3G5ZGQJOS
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
BT_TREASURY = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
USDC_ASSET = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
USD_ASSET = Asset("USD", BT_ISSUER)
USD_ASSET = Asset("TERN", "GDGQDVO6XPFSY4NMX75A7AOVYCF5JYGW2SHCJJNWCQWIDGOZB53DGP6C") # 8949 debug
MICR_TXT = f"{G_DIR}/../pii/master-identity-catalog-records.txt" #todo: modify here to load from cloud

BT_STELLAR_TOML = "https://blocktransfer.io/.well-known/stellar.toml"
OFFER_MEMO_TOML = "https://blocktransfer.io/compliance/offer-memos.toml"
WASH_SALE_TOML = "https://blocktransfer.io/compliance/wash-sales.toml"
HORIZON_INST = "https://horizon.stellar.org"
MAX_SEARCH = "limit=200"
MAX_NUM_DECIMALS = "7"
WASH_SALE_DAY_RANGE = 30
MAX_NUM_TXN_OPS = 100
BASE_FEE_MULT = 2
INVESTOR_BASE_RESERVE = Decimal("7")

server = Server(horizon_url = HORIZON_INST)
issuer = server.load_account(account_id = BT_ISSUER)
distributor = server.load_account(account_id = BT_DISTRIBUTOR)
treasury = server.load_account(account_id = BT_TREASURY)
fee = server.fetch_base_fee() * BASE_FEE_MULT

from globalToolsAssets import *
from globalToolsSearching import *
from globalToolsTransactions import *
