import sys
sys.path.append("../")
from globals import *

try:
  SECRET = sys.argv[1]
except:
  print("Running without key")

# testing: freezeBulkAssetTrustlines("StellarMart", "FREEZING: Stock split inbound")
def freezeBulkAssetTrustlines(asset, reason):
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDRarr)

def getOutstandingTrustlines(asset):
  allOutstandingTrustlines = []
  requestAddress = f"https://{HORIZON_INST}/accounts?asset={asset}:{BT_ISSUER}&limit={MAX_SEARCH}"
  data = requests.get(requestAddress).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for accounts in blockchainRecords:
      allOutstandingTrustlines.append(accounts["id"])
    # Go to next cursor
    requestAddress = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddress).json()
    blockchainRecords = data["_embedded"]["records"]
  return allOutstandingTrustlines

def signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason):
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  numTxnOps = idx = 0
  for addresses in outstandingTrustlines:
    transactions[idx].append_set_trust_line_flags_op(
      trustor = addresses,
      asset = Asset(asset, BT_ISSUER),
      clear_flags = TrustLineFlags(1),
    )
    numTxnOps += 1
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
      transactions[idx].sign(Keypair.from_secret(SECRET))
      numTxnOps = 0
      idx += 1
      appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

def exportTrustlineRevocationTransaction(txnArr):
  for txns in txnArr:
    output = open(f"{datetime.now()} signedFreezeAssetTrustlinesXDR.txt", "w")
    output.write(txns.to_xdr())
    output.close()

freezeBulkAssetTrustlines("DEMO", "Temporary freeze for split")
