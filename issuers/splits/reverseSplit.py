import requests
from datetime import datetime

searchLimitMax200 = '200'
HorizonInstance = 'horizon.stellar.org'
BTissuerAddress = 'GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7'

# testing: getMergedReportForAssetWithNumRestrictedSharesUsingMSF("StellarMart", 10000, "VeryRealStockIncMSF.csv")
# with BTissuerAddress = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM')
def reverseSplit(queryAsset, numerator, denominator):
  # FREEZE BEFOREHAND!
  # Get all account balances
  # Create burn ops per split ratio
  return didSucceed