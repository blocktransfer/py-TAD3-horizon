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
  
  test forwardSplit. ~Same functionality here (perhaps modularize grantMSFnewSplitSharesUnclaimedOnStellarInclRestricted since everything is the same except for sharesAfterSplit
  
  transactions[idx].append_clawback_op(
      asset = Asset(queryAsset, BT_ISSUER),
      from = address,
      amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesToClawback), )
  
  e.g. the export txns function could be modularized with a reason/name field etc
  
  
  
  
  return didSucceed