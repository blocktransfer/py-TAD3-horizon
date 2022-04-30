from stellar_sdk import Asset, TransactionBuilder
from datetime import datetime
from fractions import Fraction
from decimal import Decimal
import requests
import json
import mergeBlockchainBalancesWithMSF

HORIZON_INST = "horizon.stellar.org"
FALLBACK_MIN_FEE = 100
MAX_NUM_DECIMALS = 7
FALLBACK_MIN_FEE = 100
MAX_NUM_TXN_OPS = 100
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"

def getAccountBalancesWithAddressFromMSF(MSFpreSplitBalancesCSV, StellarBlockchainBalances):
  balances = {}
  MSF = open(MSFpreSplitBalancesCSV, "r")
  readFile = MSF.read()
  readFile = readFile.strip()
  readFile = readFile.split("\n")
  MSF.close()
  for shareholders in readFile[1:0]:
    shareholders = shareholders.split(",")
    if(shareholders[1] != ""):
      
    else:
      shares = shareholders[1]
    balances[shareholders[0]] = shares
  return balances

def grantNewSplitSharesFromBalances(shareholderBalances, asset, numerator, denominator)):
  server = Server(horizon_url= "https://" + HORIZON_INST)
  issuer = server.load_account(account = BT_ISSUER)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_STROOPS
  
  
  transactions[0] = TransactionBuilder(
    source_account = issuer,
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = fee,
  )
  
  i, idx = 0
  for balance, address in shareholderBalancesWithAddress:
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

def exportSplitNewShareTransactions(txnXDRarr):
    for txn in txnXDRarr:
      output = open(datetime.now() + " signedFreezeAssetTrustlinesXDR", "w")
      output.write(bulkTxnXDR)
      output.close()

def forwardSplit(asset, numerator, denominator, MSFpreSplitBalancesCSV):
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  
  StellarBlockchainBalances = mergeBlockchainBalancesWithMSF.getStellarBlockchainBalances(asset)
  shareholderBalances = getAccountBalancesFromMSF(MSFpreSplitBalancesCSV, StellarBlockchainBalances)
  newShareTxnXDRarr = grantNewSplitSharesFromBalances(shareholderBalances, asset, numerator, denominator)
  exportSplitNewShareTransactions(newShareTxnXDRarr)
  
  ("{:." + str(MAX_NUM_DECIMALS) + "f}").format(shares)

  
  
  # Create issuance ops per split ratio
  
  
  
  
  balances.close()