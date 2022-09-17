import sys
sys.path.append("../")
from globals import *
from stellar_sdk import exceptions

APPROVED_PUBLIC_KEY_CSV = f"{G_DIR}/../pii/production-approved-public-keys.csv" # just iterate through MICR?
approvalAmountXLM = Decimal("2.3")

try:
  MEMO = sys.argv[1]
except Exception:
  MEMO = "Account verified"

def createApprovedAccount():
  approvedAddrsArr = fetchNewApprovedAddrs()
  transactionsArr = buildTxnsArr(approvedAddrsArr)
  submitTxnsToStellar(transactionsArr)

def fetchNewApprovedAddrs():
  approvedAddrsCSV = open(APPROVED_PUBLIC_KEY_CSV)
  approvedAddrs = approvedAddrsCSV.read().strip().split("\n")
  approvedAddrsCSV.close()
  return approvedAddrs

def getAddress(providedAddr):
  splitAddr = providedAddr.split("*")
  if(len(splitAddr) == 1):
    return providedAddr
  elif(len(splitAddr) == 2):
    return resolveFederationAddress(providedAddr)
  else: 
    sys.exit(f"Bad address: {providedAddr}")

def seeIfAccountExists(resolvedAddr):
  try:
    server.load_account(account_id = resolvedAddr)
    return 1
  except exceptions.Ed25519PublicKeyInvalidError:
    sys.exit(f"Breaking - invalid public key: {resolvedAddr}")
  except exceptions.SdkError as error:
    if(error.status == 404):
      return 0
    else:
      sys.exit(f"Breaking - bad error from server:\n{error}")

def declareApproval(resolvedAddr, transaction):
  transaction.append_payment_op(
    destination = resolvedAddr,
    asset = Asset.native(),
    amount = approvalAmountXLM,
  )

def createAccount(resolvedAddr, transaction):
  transaction.append_create_account_op(
    destination = resolvedAddr,
    starting_balance = approvalAmountXLM
  )

def buildTxnsArr(approvedAddresses): # todo: similarly, globalize
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, treasury)
  numTxnOps = idx = 0
  for providedAddresses in approvedAddresses:
    resolvedAddresses = getAddress(providedAddresses)
    alreadyExists = seeIfAccountExists(resolvedAddresses)
    pairedInput = (resolvedAddresses, transactions[idx])
    declareApproval(*pairedInput) if alreadyExists else createAccount(*pairedInput)
    numTxnOps += 1
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(MEMO).set_timeout(30).build()
      transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
      numTxnOps = 0
      idx += 1
      appendTransactionEnvelopeToArrayWithSourceAccount(transactions, treasury)
  transactions[idx] = transactions[idx].add_text_memo(MEMO).set_timeout(30).build()
  transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
  return transactions

def submitTxnsToStellar(txnArr): # globalize
  for txns in txnArr:
    submitTxnGarunteed(txns)

createApprovedAccount()
