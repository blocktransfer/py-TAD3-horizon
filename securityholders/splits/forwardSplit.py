from stellar_sdk import Asset, TransactionBuilder
from datetime import datetime
from fractions import Fraction
from decimal import Decimal
import requests
import json

HorizonInstance = "horizon.stellar.org"
fallbackMinFeeInStroops = 100
maxNumOpsPerTxn = 100
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"

def forwardSplit(asset, numerator, denominator, preSplitBalancesCSV):
  balances = fopen(preSplitBalancesCSV, "r")
  splitRatio = Fraction(numerator, denominator)
  # Get all account balances
  
  # Create issuance ops per split ratio
  
  
  
  
  balances.close()