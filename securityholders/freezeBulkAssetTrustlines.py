import sys
sys.path.append("../")
from globals import *

# testing: freezeBulkAssetTrustlines("StellarMart", "FREEZING: Stock split inbound")
def freezeBulkAssetTrustlines(asset, reason):
  try:
    SECRET = sys.argv[1]
  except:
    print("Running without key")
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDRarr)

def getOutstandingTrustlines(asset):
  allOutstandingTrustlines = []
  requestAddress = "https://" + HORIZON_INST + "/accounts?asset=" + asset + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
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
  server = Server(horizon_url= "https://" + HORIZON_INST)
  issuer = server.load_account(account_id = BT_ISSUER)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_FEE
  transactions = []
  transactions.append(
    TransactionBuilder(
      source_account = issuer,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )
  numTxnOps = idx = 0
  for address in outstandingTrustlines:
    transactions[idx].append_set_trust_line_flags_op(
      trustor = address,
      asset = Asset(asset, BT_ISSUER),
      clear_flags = TrustLineFlags(1),
    )
    numTxnOps += 1
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
      transactions[idx].sign(Keypair.from_secret(SECRET))
      numTxnOps = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = issuer,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

def exportTrustlineRevocationTransaction(txnArr):
  for txns in txnArr:
    output = open("{} signedFreezeAssetTrustlinesXDR.txt".format(datetime.now()), "w")
    output.write(txns.to_xdr())
    output.close()

freezeBulkAssetTrustlines("DEMO", "Temporary freeze for split")
