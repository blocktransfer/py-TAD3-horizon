import sys
sys.path.append("../")
from globals import *
from stellar_sdk import exceptions
import toml

#address = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
address = "treasury*blocktransfer.io"
approvalAmountXLM = 4.2069
server = Server(horizon_url= "https://" + HORIZON_INST)
treasury = server.load_account(account_id = BT_TREASURY)
try:
  SECRET = sys.argv[1]
except Exception:
  print("Running without key")

def createApprovedAccount():
  # todo: read provided addresses from a csv of approved public keys
  providedAddr = address
  resolvedAddr = getAddress(providedAddr)
  alreadyExists = seeIfAccountExists(resolvedAddr)
  txn = declareApproval(resolvedAddr) if alreadyExists else createAccount(resolvedAddr)
  submitUnbuiltTxnToStellar(txn)

def getAddress(providedAddr):
  splitAddr = providedAddr.split("*")
  if(len(splitAddr) == 1):
    return providedAddr
  elif(len(splitAddr) == 2):
    federationName = splitAddr[0]
    federationDomain = splitAddr[1]
  else: 
    sys.exit("Bad address: {}".format(providedAddr))
  try:
    requestAddr = "https://" + federationDomain + "/.well-known/stellar.toml"
    data = toml.loads(requests.get(requestAddr).content.decode())
    homeDomainFederationServer = data["FEDERATION_SERVER"]
  except Exception:
    sys.exit("Failed to lookup federation server at {}".format(federationDomain))
  homeDomainFederationServer = homeDomainFederationServer if homeDomainFederationServer.split("/")[-1] else homeDomainFederationServer[:-1]
  requestAddr = homeDomainFederationServer + "?q=" + providedAddr + "&type=name"
  data = requests.get(requestAddr).json()
  try: 
    return data["account_id"]
  except Exception:
    sys.exit("Could not find {}".format(providedAddr))

def seeIfAccountExists(resolvedAddr):
  try:
    server.load_account(account_id = resolvedAddr)
    return 1
  except exceptions.SdkError as error:
    if(error.status == 404):
      return 0
    else:
      sys.exit("Breaking - bad error:\n{}".format(error))

def declareApproval(resolvedAddr):
  transaction = buildTxnEnv()
  transaction.append_payment_op(
    destination = resolvedAddr,
    asset = Asset.native(),
    amount = approvalAmountXLM,
  )
  return transaction

def createAccount(resolvedAddr):
  transaction = buildTxnEnv()
  transaction.append_create_account_op(
    destination = resolvedAddr,
    starting_balance = approvalAmountXLM
  )
  return transaction

def buildTxnEnv():
  try:
    minFee = server.fetch_base_fee()
  except Exception:
    minFee = FALLBACK_MIN_FEE
  transaction = TransactionBuilder(
    source_account = treasury,
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = minFee * BASE_FEE_MULT,
  )
  return transaction

def submitUnbuiltTxnToStellar(transaction):
  transaction = transaction.set_timeout(30).add_text_memo("Account passed KYC").build()
  transaction.sign(Keypair.from_secret(SECRET))
  #SERVER.submit_transaction(transaction)
  print(transaction.to_xdr())

createApprovedAccount()
