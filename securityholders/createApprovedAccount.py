import sys
sys.path.append("../")
from globals import *

address = "GD2OUJ4QKAPESM2NVGREBZTLFJYMLPCGSUHZVRMTQMF5T34UODVHPRCY"
newAccountAmount = 4.2069

server = Server(horizon_url= "https://" + HORIZON_INST)
treasury = server.load_account(account_id = BT_TREASURY)

def createApprovedAccount():
  try:
    SECRET = sys.argv[1]
  except Exception:
    print("Running without key")
  alreadyExists = seeIfAccountExists()
  txn = declareApproval() if alreadyExists else createAccount()
  submitUnbuiltTxnToStellar(txn)

def seeIfAccountExists():
  try:
    server.load_account(account_id = account)
    return 1
  except Exception:
    return 0

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
    destination = destination.public_key,
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
