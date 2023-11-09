import base64, boto3, csv, json, os.path, pandas, re, requests, sys, time, toml
import stellar_sdk as xlm
# depricated: AiohttpClient, Asset, Claimant, ClaimPredicate, Keypair, Network, Server, ServerAsync, TransactionBuilder, TrustLineFlags
# from stellar_sdk.xdr import TransactionEnvelope, TransactionResult
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from datetime import datetime, timedelta
from nameparser import HumanName
from hashlib import sha3_256
from decimal import Decimal
from pprint import pprint
TOP_DIR = os.path.dirname(__file__)
OUT_DIR = f"{TOP_DIR}/outputs"
CACHE_DIR = f"{TOP_DIR}/cache"
sys.path.append(f"{TOP_DIR}/../")
try:
  from local_secrets import *
except ModuleNotFoundError:
  TRIAL_KEY = "SBTPLXTXJDMJOXFPYU2ANLZI2ARDPHFKPKK4MJFYVZVBLXYM5AIP3LPK"
  ISSUER_KEY = DISTRIBUTOR_KEY = TREASURY_KEY = CEDE_KEY = TRIAL_KEY

BT_ISSUERS = [
  "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7",
  # Debug Issuers #
  "GCNSGHUCG5VMGLT5RIYYZSO7VQULQKAJ62QA33DBC5PPBSO57LFWVV6P", # trades
  "GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM", # accounts
  "GD7HBNPUAIK5QW7MLC7VKKHIQZCYZYCAC4YNRT3YOPYPQRK3G5ZGQJOS", # trustlines
  "GBNZILSTVQZ4R7IKQDGHYGY2QXL5QOFJYQMXPKWRRM5PAV7Y4M67AQUA"  # large sets
  "GCJKSAQECBGSLPQWAU7ME4LVQVZ6IDCNUA5NVTPPCUWZWBN5UBFMXZ53"  # AWS/'DRA'
]
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6" # This will need to be an array at >1000 client assets
BT_TREASURY = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
EMPLOYEE_COMP_CB_WITH_VOTING = "GBLOCKTRANSFER777EMPLOYEECOMPENSATION777WITHVOTING7777RV"
EMPLOYEE_COMP_CB_NO_VOTING = "GBLOCKTRANSFER777EMPLOYEECOMPENSATION777WITHOUTVOTING5M7"
USDC_ASSET = xlm.Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
BT_DOLLAR = xlm.Asset("BTD", BT_ISSUERS[0])

DEBUG_PKS = [
  "GC5TUPFLOXCINDYHQVYYLLVYP6GKHT65ELB2Q2WLFTGN63YYIXPQTDFJ", # trading
  "GAJ2HGPVZHCH6Q3HXQJMBZNIJFAHUZUGAEUQ5S7JPKDJGPVYOX54RBML", # trustlines
  "GDPA7MXCRCTY7THSCNVPQKWCPWUT7A7QJISVV5WPX6HW6ETWFW5DQIZV", # federation
  "GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG", # offer-memo cache
  "GDC4LK7ZFPEHZ6JARW72XL6IIFS7YVAQZDSTQ43THYPJMZKUTGZ3JAKA"  # not approved account
  # SCVNEA3UKCQYHQ332QENKUINKHOTPOAADERSC6SKTUQCTD7NSH3PEXFX  # ..AKA signer testing
]

# create basis DB
DIST_DATA_TOML = f"../distribution-data.toml"

BT_API_SERVER = "https://api.blocktransfer.com"
HORIZON_INST = "https://horizon.stellar.org"

ROOT_ACC_TYPES = [
  "_INDV",
  "_TST-IRV",
  "_TST-REV",
  "_TST-LIV",
  "_CO-S",
  "_CO-C",
  "_PART",
  "_ORG",
  "_PBC",
  "_GOV",
  "_ISSUER",
  "_INTERNAL",
  "_DEV"
]

BASE_FEE_MULT = 20
MAX_NUM_TXN_OPS = 100
DEF_TXN_TIMEOUT = 3600
MAX_API_BATCH_POST = 25
MAX_SUBMISSION_ATTEMPTS = 15
HIST_SAFETY_REWIND_BLOCKS = 256
MAX_PREC = Decimal("0.0000001")
INVESTOR_MIN_EXCESS_XLM = Decimal("2.1")
INVESTOR_STARTING_BAL_XLM = Decimal("4.2")
WASH_SALE_RANGE = pandas.DateOffset(days = 30)

server = xlm.Server(HORIZON_INST)
unix_base = datetime.utcfromtimestamp(0)
fee = server.fetch_base_fee() * BASE_FEE_MULT
distributor = server.load_account(account_id = BT_DISTRIBUTOR)
treasury = server.load_account(account_id = BT_TREASURY)

MM = Decimal("1000000")
REG_CF_ANNUAL_LIM = 5 * MM
RULE_701_ANNUAL_LIM = 1 * MM
SEC_4_A_5_ANNUAL_LIM = 5 * MM
REG_D_504_ANNUAL_LIM = 10 * MM
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

def requestURL(url):
  return requests.get(url).json()

def requestRecords(path, params=None):
  return requestXLM(path, params)["_embedded"]["records"]

def requestXLM(path, params={}):
  params["limit"] = 200
  data = requests.get(
    f"{HORIZON_INST}/{path}",
    params = params
  ).json()
  try:
    return returnLedgerIfNotRateLimited(data)
  except LookupError:
    return requestXLM(path, params)

def returnLedgerIfNotRateLimited(ledger):
  try:
    if(ledger["status"]):
      time.sleep(250)
      raise LookupError
  except KeyError:
    return ledger

# replace with a default error
class PagignationIncomplete(Exception):
  pass

def requestAWS(path, params=None):
  data = requests.get(
    f"{BT_API_SERVER}/{path}",
    auth = getIAMenvAuth(),
    params = params
  ).json()
  try:
    return returnAPIresponseIfComplete(data)
  except PagignationIncomplete:
    return requestAWS(path, params)

def returnAPIresponseIfComplete(response):
  # if ( response LastItem ):
  #   implement recursive pagination
  #   response[].append(requestAWS(_next))
  
  # in Lambda? 
  #
  return response

def postAWS(path, data):
  return requests.post(
    f"{BT_API_SERVER}/{path}",
    data = json.dumps(data),
    auth = getIAMenvAuth()
  ).json()

def getIAMenvAuth():
  return BotoAWSRequestsAuth(
    aws_host = BT_API_SERVER[8:],
    aws_region = "us-east-2",
    aws_service = "execute-api"
  )

def getLinksAndRecordsFromParsedLedger(data):
  return data["_links"], data["_embedded"]["records"]

def SHA3(input):
  return sha3_256(input.encode()).hexdigest()

from globalToolsTransactions import *
from globalToolsSearching import *
from globalToolsAssets import *

# Key stock data functions #
def getNumOutstandingShares(queryAsset):
  assetData = requestAssetRecords(queryAsset)
  shares = Decimal(assetData["liquidity_pools_amount"])
  for balances in assetData["balances"].values():
    shares += Decimal(balances)
  shares += Decimal(assetData["claimable_balances_amount"])
  companyCode = getCompanyCodeFromAssetCode(queryAsset)
  return shares - getNumAuthorizedSharesNotIssued(companyCode, queryAsset)

def getFloat(queryAsset):
  url = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={getAssetIssuer(queryAsset)}"
  assetData = requestRecords(url)[0]
  tradingAMMshares = Decimal(assetData["liquidity_pools_amount"])
  outstandingSharesTradable = Decimal(assetData["amount"])
  shares = tradingAMMshares + outstandingSharesTradable
  # CHANGE HERE TO UPDATED COMPANY ACCOUNT QUERIES
  return shares - getAffiliateShares(queryAsset)

