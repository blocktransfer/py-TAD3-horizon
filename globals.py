import asyncio, functools, json, os.path, pandas, requests, sys, toml
from stellar_sdk.xdr import TransactionResult
from datetime import datetime
from hashlib import sha3_256
from decimal import Decimal
from pprint import pprint
from stellar_sdk import (
  AiohttpClient,
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
# Issuing memos:
# {New/IPO} stock: {S-{formType}||A-1} ({regFile#wDash})
# or New private stock ({CIKwithoutLeadingZeros})
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
BT_TREASURY = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
USDC_ASSET = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
BT_DOLLAR = Asset("BTD", BT_ISSUER)

BT_WEB = "https://blocktransfer.io"
BT_STELLAR_TOML = f"{BT_WEB}/.well-known/stellar.toml"
BT_ACCOUNTS_TOML = f"{BT_WEB}/.well-known/accounts.toml"
OFFER_MEMO_TOML = f"{BT_WEB}/caching-data/offer-memos.toml" #
WASH_SALE_TOML = f"{BT_WEB}/caching-data/wash-sales.toml" # localize these 
HORIZON_INST = "https://horizon.stellar.org"
MAX_SEARCH = "limit=200"

BASE_FEE_MULT = 20
MAX_NUM_TXN_OPS = 100
WASH_SALE_DAY_RANGE = 30
MAX_SUBMISSION_ATTEMPTS = 15
MAX_PREC = Decimal("0.0000001")
INVESTOR_MIN_EXCESS = Decimal("2.1")
INVESTOR_STARTING_BAL = Decimal("4.2")

unix_base = datetime.utcfromtimestamp(0)
server = Server(horizon_url = HORIZON_INST)
fee = server.fetch_base_fee() * BASE_FEE_MULT
issuer = server.load_account(account_id = BT_ISSUER)
distributor = server.load_account(account_id = BT_DISTRIBUTOR)
treasury = server.load_account(account_id = BT_TREASURY)

MM = Decimal("1000000")
REG_CF_ANNUAL_LIM = 5 * MM
RULE_701_ANNUAL_LIM = 1 * MM
REG_D_504_ANNUAL_LIM = 10 * MM
SECTION_4_A_5_ANNUAL_LIM = 5 * MM
REG_A_TIER_1_ANNUAL_LIM = 20 * MM
REG_A_TIER_2_ANNUAL_LIM = 75 * MM

# localize these?
REG_CF_STD_LIM = Decimal("2500")
REG_D_506_B_NON_ACCREDITED_INVESTOR_LIM = 35
FIRM_AFFILIATE_LOOKBACK = pandas.DateOffset(days = 90)
IPO_LOCKUP_MAX_OVERRIDE = pandas.DateOffset(days = 90)
IPO_NOT_AFFILIATED_RESTRICTION = pandas.DateOffset(days = 90)
RULE_144_HOLDING_MIN_REPORTING_CO = pandas.DateOffset(months = 6)
RULE_144_HOLDING_MIN_NOT_REPORTING = pandas.DateOffset(years = 1)
RULE_144_MIN_REPORTING_QUALIFICATION_TIME = pandas.DateOffset(days = 90)
RULE_144_MIN_REPORTING_SHARES = Decimal("5000")
RULE_144_MIN_REPORTING_USD_VAL = Decimal("50000")
RULE_144_NOT_AFFILIATED_PERIOD = pandas.DateOffset(months = 3)
RULE_144_SALE_REPORTING_PERIOD = pandas.DateOffset(months = 3)
THRESHOLD_FOR_AFFILIATE_VIA_PERCENT_FLOAT_OWNED = Decimal("0.1")

from globalToolsAssets import *
from globalToolsSearching import *
from globalToolsTransactions import *

def getNumOutstandingShares(queryAsset):
  assetAddr = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  assetData = requests.get(assetAddr).json()["_embedded"]["records"][0]
  shares = Decimal(assetData["liquidity_pools_amount"])
  for balances in assetData["balances"].values():  
    shares += Decimal(balances)
  shares += Decimal(assetData["claimable_balances_amount"])
  companyCode = getCompanyCodeFromAssetCode(queryAsset)
  return shares - getNumAuthorizedSharesNotIssued(companyCode)

def getFloat(queryAsset):
  assetAddr = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  unrestricted = requests.get(assetAddr).json()["_embedded"]["records"][0][amount]
  return unrestricted - getAffiliateShares(queryAsset)

getAffiliateShares("DEMO")