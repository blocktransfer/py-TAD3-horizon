import sys
sys.path.append("../")
from globals import *

FREEZING = ""

# testing: freezeBulkAssetTrustlines("StellarMart", "Freezing all accounts prior 5-to-2 forward stock split. Adjust future offers accordingly")
def freezeBulkAssetTrustlines(asset, reason):
  try:
    SECRET = sys.argv[1]
  except:
    print("Running without key")
  FREEZING = asset
  outstandingTrustlines = getOutstandingTrustlinesForFreezingAsset()
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDRarr)

def getOutstandingTrustlinesForFreezingAsset():
  requestAddress = "https://" + HORIZON_INST + "..." + BT_ISSUER + "..."
  data = requests.get(requestAddress).json()
  
  allOutstandingTrustlines = []
  outstandingTrustline = data[...]
  while(outstandingTrustline):
    address = outstandingTrustline[...]
    outstandingTrustline.append(address)
    
    requestAddress = "https://" + HORIZON_INST + "..." + BT_ISSUER + "..." -> next
    data = requests.get(requestAddress).json()
    outstandingTrustline = data[...]

  return allOutstandingTrustlines

def signBulkTrustlineRevocationTxn(outstandingTrustlines, reason):
  server = Server(horizon_url= "https://" + HORIZON_INST)
  issuer = server.load_account(account = BT_ISSUER)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_FEE
  transactions = []
  transactions[0] = TransactionBuilder(
    source_account = issuer,
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = fee,
  )
  numTxnOps, idx = 0
  for address in outstandingTrustlines:
    transactions[idx].append_set_trust_line_flags_op(
      trustor = address,
      asset = Asset(FREEZING, BT_ISSUER),
      clear_flags = 1
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
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()\
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

def exportTrustlineRevocationTransaction(txnArr):
  for txns in txnArr:
    output = open(str(datetime.now()) + " signedFreezeAssetTrustlinesXDR.txt", "w")
    output.write(txns.to_xdr())
    output.close()

