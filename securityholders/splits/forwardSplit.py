from stellar_sdk import Asset, TransactionBuilder
from datetime import datetime
from fractions import Fraction
from decimal import Decimal
import requests
import json

HorizonInstance = "horizon.stellar.org"
fallbackMinFeeInStroops = 100
MAX_NUM_DECIMALS = 7
MAX_NUM_TXN_OPS = 100
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"

def getAccountBalancesFromMSF(preSplitBalancesCSV):
  MSF = open(preSplitBalancesCSV, "r")
  shareholder = MSF.readline().readline()
  balances[] = ""
  while(shareholder):
    balances.append(shareholder[0])
    shareholder = MSF.readline()
  MSF.close()
  return balances



def exportSplitNewShareTransactions(txnXDRarr):
    for txn in txnXDRarr:
      output = open(datetime.now() + " signedFreezeAssetTrustlinesXDR", "w")
      output.write(bulkTxnXDR)
      output.close()

def forwardSplit(asset, numerator, denominator, preSplitBalancesCSV):
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  
  
  shareholderBalances = getAccountBalancesFromMSF(preSplitBalancesCSV)
  newShareTxnXDRarr = grantNewSplitSharesFromBalances(shareholderBalances)
  exportSplitNewShareTransactions(newShareTxnXDRarr)
  
  ("{:." + str(MAX_NUM_DECIMALS) + "f}").format(shares)

  
  
  # Create issuance ops per split ratio
  
  
  
  
  balances.close()