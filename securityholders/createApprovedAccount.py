import sys
sys.path.append("../")
from globals import *
from stellar_sdk import exceptions

APPROVED_PUBLIC_KEY_CSV = "exampleListApprovedAddresses.csv"
approvalAmountXLM = Decimal("4.2069")
try:
  SECRET = sys.argv[1]
except Exception:
  print("Running without key")

def createApprovedAccount():
  approvedAddressesArr = fetchApprovedAddrFromCSV()
  transactionsArr = buildTxnsArr(approvedAddressesArr)
  submitTxnsToStellar(transactionsArr)

def fetchApprovedAddrFromCSV():
  addrCSV = open(MICR)
  approvedAddr = addrCSV.read().strip().split("\n")
  addrCSV.close()
  return approvedAddr

def getAddress(providedAddr):
  splitAddr = providedAddr.split("*")
  if(len(splitAddr) == 1):
    return providedAddr
  elif(len(splitAddr) == 2):
    return resolveFederationAddress(providedAddr)
  else: 
    sys.exit("Bad address: {}".format(providedAddr))

def seeIfAccountExists(resolvedAddr):
  try:
    server.load_account(account_id = resolvedAddr)
    return 1
  except exceptions.Ed25519PublicKeyInvalidError:
    sys.exit("Breaking - invalid public key: {}".format(resolvedAddr))
  except exceptions.SdkError as error:
    if(error.status == 404):
      return 0
    else:
      sys.exit("Breaking - bad error from server:\n{}".format(error))

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

def buildTxnsArr(approvedAddresses):
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
      transactions[idx] = transactions[idx].add_text_memo("Account passed KYC").set_timeout(30).build()
      transactions[idx].sign(Keypair.from_secret(SECRET))
      numTxnOps = 0
      idx += 1
      appendTransactionEnvelopeToArrayWithSourceAccount(transactions, treasury)
  transactions[idx] = transactions[idx].add_text_memo("Account passed KYC").set_timeout(30).build()
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

def submitTxnsToStellar(txnArr):
  for txns in txnArr:
    print("Transaction:")
    print(txns.to_xdr())
    #submitTxnGarunteed(transaction)

createApprovedAccount()
