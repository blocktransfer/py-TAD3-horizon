import sys
sys.path.append("../")
from globals import *

# testing: freezeBulkAssetTrustlines("StellarMart", "FREEZING: Stock split inbound")
def freezeBulkAssetTrustlines(asset, reason):
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDRarr)

def getOutstandingTrustlines(queryAsset):
  allOutstandingTrustlines = []
  requestAddr = getAssetAccountsAddress(queryAsset)
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for accounts in ledger["_embedded"]["records"]:
      allOutstandingTrustlines.append(accounts["id"])
    ledger = getNextLedgerData(ledger)
  return allOutstandingTrustlines

def signBulkTrustlineRevocationTxn(outstandingTrustlines, queryAsset, reason):
  transactions = []
  issuer = getAssetIssuer(queryAsset)
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  numTxnOps = idx = 0
  for addresses in outstandingTrustlines:
    transactions[idx].append_set_trust_line_flags_op(
      trustor = addresses,
      asset = getAssetObjFromCode(queryAsset),
      clear_flags = TrustLineFlags(1),
    )
    numTxnOps += 1
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
      transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
      numTxnOps = 0
      idx += 1
      appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
  transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
  return transactions

def exportTrustlineRevocationTransaction(txnArr):
  for txns in txnArr:
    with open(f"{datetime.now()} signedFreezeAssetTrustlinesXDR.txt", "w") as output:
      output.write(txns.to_xdr())

freezeBulkAssetTrustlines("DEMO", "Temporary freeze for split")
