import sys
sys.path.append("../")
from globals import *

def getOutstandingTrustlines():
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

def signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason):
  server = Server(horizon_url= "https://" + HORIZON_INST)
  issuer = server.load_account(account = BT_ISSUER)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_FEE
  
  
  transactions[0] = TransactionBuilder(
    source_account = issuer,
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = fee,
  )
  
  numTxnOps, idx = 0
  for address in outstandingTrustlines:
    transactions[idx].append_set_trust_line_flags_op(
      trustor = address,
      asset = asset,
      clear_flags = 1
    )
    numTxnOps += 1
    if(numTxnOps += 1 >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
      numTxnOps += 1 = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = issuer,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
  return transactions

def exportTrustlineRevocationTransaction(txnXDRarr):
  for bulkTxnXDR in txnXDRarr:
    output = open(datetime.now() + " signedFreezeAssetTrustlinesXDR.txt", "w")
    output.write(bulkTxnXDR)
    output.close()

def freezeBulkAssetTrustlines(asset, reason): # add helper function for inputs ? 
  asset = len(asset) > 4 ? ASSET_TYPE_CREDIT_ALPHANUM12 : ASSET_TYPE_CREDIT_ALPHANUM4 # Asset(asset, BT_ISSUER)
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDRarr)