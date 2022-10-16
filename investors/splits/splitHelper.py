import sys
sys.path.append("../../")
from globals import *

def generatePostSplitMSF(MSFpreSplitBalancesTXT, numerator, denominator, postSplitFileName):
  oldMSF = open(MSFpreSplitBalancesTXT)
  newMSF = open(postSplitFileName, "w")
  newMSF.write(next(oldMSF) + "\n")
  for accounts in oldMSF:
    account = accounts.split("|")
    if(account[1]):
      sharesAfterSplit = Decimal(account[1]) * numerator / denominator
      account[1] = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesAfterSplit)
      newMSF.write(f"{'|'.join(account)}\n")
    else:
      newMSF.write(f"{'|'.join(account)}\n")
  oldMSF.close()
  newMSF.close()
  return newMSF

def exportSplitNewShareTransactions(txnArr, queryAsset):
  for txns in txnArr:
    output = open(f"{str(datetime.now()).replace(':','.')} {queryAsset} StockSplitOutputXDR.txt", "w")
    output.write(txns.to_xdr())
    output.close()

# for dynamic claimable stock grants:
def fetchClaimableBalances(queryAsset):
    return 1
# clawback / create new distributor (same basis) claimiable balalnce in fwd/rvs code
