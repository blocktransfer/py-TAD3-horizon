import sys
sys.path.append("../")
from globals import *
from stellar_sdk import exceptions

address = "GBX3X43Q44RLZTTVQYY5VI3XIRZGCE4S52MTBQUY7ZZM2PSKEHFCY35N"
newAccountAmount = 4.2069

server = Server(horizon_url= "https://" + HORIZON_INST)
treasury = server.load_account(account_id = BT_TREASURY)

def createApprovedAccount():
  try:
    SECRET = sys.argv[1]
  except Exception:
    print("Running without key")
  alreadyExists = seeIfAccountExists()
  print(alreadyExists)
  return 1
  txn = declareApproval() if alreadyExists else createAccount()
  submitUnbuiltTxnToStellar(txn)

def seeIfAccountExists():
  try:
    server.load_account(account_id = address)
    return 1
  except exceptions.SdkError as error:
    if(error.status == 404):
      return 0
    else:
      sys.exit("Breaking - bad error:\n{}".format(error))

def declareApproval():
  transaction = buildTxnEnv()
  transaction.append_payment_op(
    destination = address,
    asset = Asset.native(),
    amount = newAccountAmount,
  )
  return transaction

def createAccount():
  transaction = buildTxnEnv()
  transaction.append_create_account_op(
    destination = address,
    starting_balance = newAccountAmount
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
