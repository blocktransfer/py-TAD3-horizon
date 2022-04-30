from stellar_sdk import Asset, Keypair, Server, TransactionBuilder
from datetime import datetime
import requests
import json

searchLimitMax200 = "200" # rem as needed

secretKey = ""

HORIZON_INST = "horizon.stellar.org"
FALLBACK_MIN_FEE = 100
MAX_NUM_TXN_OPS = 100
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"

def getOutstandingTrustlines():
  r = "https://" + HORIZON_INST + "..." + BT_ISSUER + "..."
  data = r.json()
  
  allOutstandingTrustlines = []
  outstandingTrustline = data[...]
  while(outstandingTrustline):
    address = outstandingTrustline[...]
    outstandingTrustline.append(address)
    
    r = "https://" + HORIZON_INST + "..." + BT_ISSUER + "..." -> next
    data = r.json()
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
  
  i, idx = 0
  for address in outstandingTrustlines:
    transactions[idx].append_set_trust_line_flags_op(
      trustor = address,
      asset = asset,
      clear_flags = 1
    )
    if(++i and i >= MAX_NUM_TXN_OPS):
      transactions[idx].add_text_memo(reason).set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
      i = 0
      idx++
      transactions[idx] = TransactionBuilder( # todo: might need to do append() here 
        source_account = issuer,
        network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
        base_fee = fee,
      )
  transactions[idx].add_text_memo(reason).set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
  return transactions

def exportTrustlineRevocationTransaction(txnXDRarr):
    for txn in txnXDRarr:
      output = open(datetime.now() + " signedFreezeAssetTrustlinesXDR", "w")
      output.write(bulkTxnXDR)
      output.close()

def freezeBulkAssetTrustlines(asset, reason): # add helper function for inputs ? 
  asset = len(asset) > 4 ? ASSET_TYPE_CREDIT_ALPHANUM12 : ASSET_TYPE_CREDIT_ALPHANUM4 # Asset(asset, BT_ISSUER)
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDRarr = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDRarr)