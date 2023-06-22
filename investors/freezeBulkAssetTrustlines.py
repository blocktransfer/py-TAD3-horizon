import sys
sys.path.append("../")
from globals import *
from trustlineHelper import *

def freezeBulkAssetTrustlines(asset, reason):
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportBulkTrustlineTransactionsXDR(revocationTxnXDRarr)

def getOutstandingTrustlines(queryAsset):
  allOutstandingTrustlinesForAsset = []
  ledger = requestAssetAccounts(queryAsset)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  while(records):
    for accounts in records:
      allOutstandingTrustlinesForAsset.append(accounts["id"])
    links, records = getNextLedgerData(links)
  return allOutstandingTrustlinesForAsset

def signBulkTrustlineRevocationTxn(outstandingTrustlines, queryAsset, reason):
  transactions = []
  issuer = getIssuerAccObj(queryAsset)
  issuerSigner = Keypair.from_secret(ISSUER_KEY)
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
      transactions[idx] = prepTxn(transactions[idx], reason, issuerSigner)
      numTxnOps = 0
      idx += 1
      appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = prepTxn(transactions[idx], reason, issuerSigner)
  return transactions


# testing: freezeBulkAssetTrustlines("StellarMart", "FREEZING: Stock split inbound")
freezeBulkAssetTrustlines("DEMO", "Temporary freeze for split")
