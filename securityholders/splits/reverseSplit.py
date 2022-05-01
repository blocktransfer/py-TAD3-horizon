import sys
sys.path.append("../../")
from globals import *

postSplitFileName = "[BACKWARDS] {} Post-Split Master Securityholder File.csv"

def reverseSplit(queryAsset, numerator, denominator):
  
  # Create burn ops per split ratio
  transactions[idx].append_clawback_op(
      asset = Asset(queryAsset, BT_ISSUER),
      from = address,
      amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesToClawback), )  



copy/paste forward split 
