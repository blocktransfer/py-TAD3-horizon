import asyncio, functools, json, os.path, pandas, requests, sys, toml
from stellar_sdk.xdr import TransactionEnvelope, TransactionResult
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
  ServerAsync,
  TransactionBuilder,
  TrustLineFlags
)
TOP_DIR = os.path.dirname(__file__)
sys.path.append(f"{TOP_DIR}/../")
MICR_DIR = f"{TOP_DIR}/../master-identity-catalog-records"
MICR_TXT = f"{MICR_DIR}/master-identity-account-mapping.txt"
try:
  from local_secrets import *
except ModuleNotFoundError:
  TRIAL_KEY = "SBTPLXTXJDMJOXFPYU2ANLZI2ARDPHFKPKK4MJFYVZVBLXYM5AIP3LPK"
  ISSUER_KEY = DISTRIBUTOR_KEY = TREASURY_KEY = CEDE_KEY = TRIAL_KEY

BT_ISSUERS = [
"GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7",
"GCNSGHUCG5VMGLT5RIYYZSO7VQULQKAJ62QA33DBC5PPBSO57LFWVV6P", # debug: trades
"GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM", # debug: accounts
"GD7HBNPUAIK5QW7MLC7VKKHIQZCYZYCAC4YNRT3YOPYPQRK3G5ZGQJOS", # debug: trustlines
"GBNZILSTVQZ4R7IKQDGHYGY2QXL5QOFJYQMXPKWRRM5PAV7Y4M67AQUA" # debug: large sets
]
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"
BT_TREASURY = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
EMPLOYEE_COMP_CB_WITH_VOTING = "GBLOCKTRANSFER777EMPLOYEECOMPENSATION777WITHVOTING7777RV"
EMPLOYEE_COMP_CB_NO_VOTING = "GBLOCKTRANSFER777EMPLOYEECOMPENSATION777WITHOUTVOTING5M7"
USDC_ASSET = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
BT_DOLLAR = Asset("BTD", BT_ISSUERS[0])

BT_WELL_KNOWN = "https://blocktransfer.io/.well-known"
BT_STELLAR_TOML = f"{BT_WELL_KNOWN}/stellar.toml"
BT_ACCOUNTS_TOML = f"{BT_WELL_KNOWN}/accounts.toml"
OFFER_MEMO_TOML = f"{BT_WELL_KNOWN}/xlm-cache/offer-memos.toml"
WASH_SALE_TOML = f"{BT_WELL_KNOWN}/xlm-cache/wash-sales.toml"
DIST_DATA_TOML = f"{BT_WELL_KNOWN}/distribution-data.toml"
HORIZON_INST = "https://horizon.stellar.org"
MAX_SEARCH = "limit=200"

BASE_FEE_MULT = 20
MAX_NUM_TXN_OPS = 100
DEF_TXN_TIMEOUT = 3600
WASH_SALE_DAY_RANGE = 30
MAX_SUBMISSION_ATTEMPTS = 15
MAX_PREC = Decimal("0.0000001")
INVESTOR_MIN_EXCESS = Decimal("2.1")
INVESTOR_STARTING_BAL = Decimal("4.2")

server = Server(HORIZON_INST)
unix_base = datetime.utcfromtimestamp(0)
fee = server.fetch_base_fee() * BASE_FEE_MULT
distributor = server.load_account(account_id = BT_DISTRIBUTOR)
treasury = server.load_account(account_id = BT_TREASURY)

MM = Decimal("1000000")
REG_CF_ANNUAL_LIM = 5 * MM
RULE_701_ANNUAL_LIM = 1 * MM
REG_D_504_ANNUAL_LIM = 10 * MM
SECTION_4_A_5_ANNUAL_LIM = 5 * MM
REG_A_TIER_1_ANNUAL_LIM = 20 * MM
REG_A_TIER_2_ANNUAL_LIM = 75 * MM

# -> portal repo:
RULE_144_SALE_REPORTING_PERIOD = pandas.DateOffset(months = 3)
RULE_144_MIN_AFF_REPORTING_USD_THRESH_PER_PERIOD = Decimal("50000")
RULE_144_MIN_AFF_REPORTING_SHARES_THRESH_PER_PERIOD = Decimal("5000")
# -> app repo:
RULE_144_REPORTING_CO_HOLDING_MIN = pandas.DateOffset(months = 6)
RULE_144_NOT_REPORTING_HOLDING_MIN = pandas.DateOffset(years = 1)
RULE_144_AFFILIATE_LOOKBACK_PERIOD = pandas.DateOffset(months = 3)
RULE_144_MIN_REPORTING_QUALIFICATION_TIME = pandas.DateOffset(days = 90) # this doesn't have anything to compare to using bool reporting scheme
# todo: implement IPO logic in /issuers
IPO_OLD_SHARES_MIN_LOCKUP = pandas.DateOffset(days = 90)

REG_CF_STD_LIM = Decimal("2500")
REG_D_506B_NON_ACCREDITED_INVESTOR_LIM = 35
REG_A_TIER_1_YR_1_MONTHLY_SALE_MAX = 6 * MM
NON_REPORTING_CO_TOTAL_ASSETS_MAX = 10 * MM
NON_REPORTING_CO_TOTAL_INVESTORS_MAX = 2000
NON_REPORTING_CO_NON_ACCREDITED_INVESTOR_MAX = 500
AFFILIATE_VIA_PERCENT_FLOAT_OWNED_MIN = Decimal("0.1")

class RateLimited(Exception):
  pass

def requestURL(url):
  return requests.get(url).json()

def requestRecords(url):
  return requestURL(url)["_embedded"]["records"]

def getLinksAndRecordsFromParsedLedger(data):
  return data["_links"], data["_embedded"]["records"]

def SHA3(input):
  return sha3_256(input.encode()).hexdigest()

from globalToolsTransactions import *
from globalToolsSearching import *
from globalToolsAssets import *
from globalToolsDebug import *

def getNumOutstandingShares(queryAsset):
  assetData = requestAssetRecords(queryAsset)
  shares = Decimal(assetData["liquidity_pools_amount"])
  for balances in assetData["balances"].values():
    shares += Decimal(balances)
  shares += Decimal(assetData["claimable_balances_amount"])
  companyCode = getCompanyCodeFromAssetCode(queryAsset)
  return shares - getNumAuthorizedSharesNotIssued(companyCode, queryAsset)

def getFloat(queryAsset):
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  assetData = requestRecords(url)[0]
  tradingAMMshares = Decimal(assetData["liquidity_pools_amount"])
  outstandingSharesTradable = Decimal(assetData["amount"])
  shares = tradingAMMshares + outstandingSharesTradable
  # CHANGE HERE TO UPDATED COMPANY ACCOUNT QUERIES
  return shares - getAffiliateShares(queryAsset)

