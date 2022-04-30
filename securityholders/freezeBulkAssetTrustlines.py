from stellar_sdk import Asset, TransactionBuilder
from datetime import datetime
import requests
import json

searchLimitMax200 = "200" # rem as needed

HorizonInstance = "horizon.stellar.org"
fallbackMinFeeInStroops = 100
MAX_NUM_TXN_OPS = 100
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"

def getOutstandingTrustlines():
  r = "https://" + HorizonInstance + "..." + BT_ISSUER + "..."
  data = r.json()
  
  allOutstandingTrustlines = []
  outstandingTrustline = data[...]
  while(outstandingTrustline):
    address = outstandingTrustline[...]
    outstandingTrustline.append(address)
    
    r = "https://" + HorizonInstance + "..." + BT_ISSUER + "..." -> next
    data = r.json()
    outstandingTrustline = data[...]

  return allOutstandingTrustlines

def signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason):
  server = Server(horizon_url= "https://" + HorizonInstance)
  issuer = server.load_account(account = BT_ISSUER)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = fallbackMinFeeInStroops
  
  
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
        # todo: cleanup after verf
    )
    if(++i and i >= MAX_NUM_TXN_OPS):
      i = 0
      idx++
      transactions[idx] = TransactionBuilder(
        source_account = issuer,
        network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
        base_fee = fee,
      )

  for tnx in transactions:
    tnx.add_text_memo(reason).set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
  
  return transactions

def exportTrustlineRevocationTransaction(bulkTxnXDR):
    output = fopen(datetime.now() + " signedFreezeAssetTrustlinesXDR", "w")
    output.write(bulkTxnXDR)
    output.close()

def freezeBulkAssetTrustlines(asset, reason): # add helper function for inputs ? 
  asset = len(asset) > 4 ? ASSET_TYPE_CREDIT_ALPHANUM12 : ASSET_TYPE_CREDIT_ALPHANUM4 # Asset(asset, BT_ISSUER)
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxnXDR = signBulkTrustlineRevocationTxn(outstandingTrustlines, asset, reason)
  exportTrustlineRevocationTransaction(revocationTxnXDR)