import sys
sys.path.append("../")
from globals import *

try:
  MEMO = sys.argv[1]
except Exception: ###
  MEMO = "Account Verified ✔️"

def createApprovedAccount():
  approvedAddrsArr = getValidAccountPublicKeys()
  transactionsArr = buildTxnsArr(approvedAddrsArr)
  submitTxnsToStellar(transactionsArr)
#
def getAddress(providedAddr):
  splitAddr = providedAddr.split("*")
  if(len(splitAddr) == 1):
    return providedAddr
  if(len(splitAddr) == 2):
    return resolveFederationAddress(providedAddr)
  sys.exit(f"Bad address: {providedAddr}")

def seeIfAccountExists(resolvedAddr):
  try:
    server.load_account(account_id = resolvedAddr)
    return 1
  except xdr.exceptions.Ed25519PublicKeyInvalidError:
    sys.exit(f"Breaking - invalid public key: {resolvedAddr}")
  except xdr.exceptions.SdkError as error:
    if(error.status == 404):
      return 0
    else:
      sys.exit(f"Breaking - bad error from server:\n{error}")

def declareApproval(resolvedAddr, transaction):
  transaction.append_payment_op(
    destination = resolvedAddr,
    asset = Asset.native(),
    amount = INVESTOR_BASE_RESERVE,
  )

def createAccount(resolvedAddr, transaction):
  transaction.append_create_account_op(
    destination = resolvedAddr,
    starting_balance = approvalAmountXLM
  )

def buildTxnsArr(approvedAddrs): # todo: similarly, globalize
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, treasury)
  numTxnOps = idx = 0
  for providedAddrs in approvedAddrs:
    resolvedAddr = getAddress(providedAddrs)
    alreadyExists = seeIfAccountExists(resolvedAddr)
    packedInput = (resolvedAddr, transactions[idx])
    declareApproval(*packedInput) if alreadyExists else createAccount(*packedInput)
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

# distributeLegacyShares