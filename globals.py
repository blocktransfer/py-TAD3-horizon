import functools, json, os.path, pandas, requests, sys, toml
from stellar_sdk.xdr import TransactionResult
from datetime import datetime
from decimal import Decimal
from pprint import pprint
from stellar_sdk import (
  Asset,
  Claimant,
  ClaimPredicate,
  Keypair,
  Network,
  Server,
  TransactionBuilder,
  TrustLineFlags
)
sys.path.append("../")
G_DIR = os.path.dirname(__file__)
MICR_DIR = f"{G_DIR}/../master-identity-catalog-records"
MICR_TXT = f"{MICR_DIR}/master-identity-account-mapping.txt"
try:
  from local_secrets import *
except ModuleNotFoundError:
  TRIAL_KEY = "SBTPLXTXJDMJOXFPYU2ANLZI2ARDPHFKPKK4MJFYVZVBLXYM5AIP3LPK"
  ISSUER_KEY = DISTRIBUTOR_KEY = TREASURY_KEY = CEDE_KEY = TRIAL_KEY

# Debug issuers:
# accounts - GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM
# trustlines - GD7HBNPUAIK5QW7MLC7VKKHIQZCYZYCAC4YNRT3YOPYPQRK3G5ZGQJOS
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
BT_TREASURY = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
USDC_ASSET = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
BT_DOLLAR = Asset("BTD", BT_ISSUER)

BT_WEB = "https://blocktransfer.io"
BT_STELLAR_TOML = f"{BT_WEB}/.well-known/stellar.toml"
OFFER_MEMO_TOML = f"{BT_WEB}/caching-data/offer-memos.toml"
WASH_SALE_TOML = f"{BT_WEB}/caching-data/wash-sales.toml"
HORIZON_INST = "https://horizon.stellar.org"
MAX_SEARCH = "limit=200"
WASH_SALE_DAY_RANGE = 30
MAX_NUM_TXN_OPS = 100
BASE_FEE_MULT = 2
MAX_PREC = Decimal("0.0000001")
INVESTOR_BASE_RESERVE = Decimal("7")

server = Server(horizon_url = HORIZON_INST)
issuer = server.load_account(account_id = BT_ISSUER)
distributor = server.load_account(account_id = BT_DISTRIBUTOR)
treasury = server.load_account(account_id = BT_TREASURY)
fee = server.fetch_base_fee() * BASE_FEE_MULT

from globalToolsAssets import *
from globalToolsSearching import *
from globalToolsTransactions import *

def getNumOutstandingShares(queryAsset, numComplexOfflineRestrictedShares):
  tokens = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  numUnrestrictedShares = requests.get(tokens).json()["_embedded"]["records"][0]["amount"] # testing: this should include CBs directly from issuer in the case of modified restricted shares during reverse splits
  totalOutstandingShares = Decimal(numUnrestrictedShares) + Decimal(numComplexOfflineRestrictedShares)
  treasuryShares = getNumTreasuryShares(queryAsset)
  employeeBenefitShares = getNumEmployeeBenefitShares(queryAsset)
  return totalOutstandingShares - treasuryShares - employeeBenefitShares

# todo: change distributions from payments to CBs so that accounts don't need trustlines with all issuer assets