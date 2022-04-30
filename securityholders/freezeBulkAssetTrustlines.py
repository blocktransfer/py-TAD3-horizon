from stellar_sdk import Asset, TransactionBuilder
from datetime import datetime
import requests
import json

searchLimitMax200 = "200"
HorizonInstance = "horizon.stellar.org"
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





def freezeBulkAssetTrustlines(asset):
  asset = len(asset) > 4 ? ASSET_TYPE_CREDIT_ALPHANUM12 : ASSET_TYPE_CREDIT_ALPHANUM4 # Asset(asset, BT_ISSUER)
  outstandingTrustlines = getOutstandingTrustlines(asset)
  revocationTxn = buildRevocationTxn(outstandingTrustlines)