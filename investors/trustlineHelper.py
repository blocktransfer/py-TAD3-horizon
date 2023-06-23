import sys
sys.path.append("../")
from globals import *

# todo: replace with submit to network func in global assets
def exportBulkTrustlineTransactionsXDR(txnXDRarr):
  type = ""
  path = f"{TOP_DIR}/outputs/"
  for txn in txnXDRarr:
    if(not type):
      try:
        allowingTrust = txn.transaction.operations[0].set_flags
      except AttributeError:
        sys.exit("No trustline transactions given.")
      if(allowingTrust):
        type = "ApprovePending"
      else:
        type = "FreezeAsset"
    time = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
    name = f"{time} signed{type}TrustlinesXDR.txt"
    with open(path + name, "w") as output:
      output.write(txn.to_xdr())

