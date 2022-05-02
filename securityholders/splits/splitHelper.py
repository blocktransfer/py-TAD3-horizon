import sys
sys.path.append("../../")
from globals import *

def generatePostSplitMSFupdatingInvestorsUnclaimedOnStellarInclRestricted(MSFpreSplitBalancesCSV, numerator, denominator, postSplitFileName):
  MSF = open(MSFpreSplitBalancesCSV, "r")
  oldMSF = MSF.read()
  oldMSF = oldMSF.strip()
  oldMSF = oldMSF.split("\n")
  MSF.close()
  newMSF = open(postSplitFileName, "w")
  newMSF.write(oldMSF[0] + "\n")
  for shareholder in oldMSF[1:]: # Assume separate restricted and unrestricted entries
    shareholder = shareholder.split(",")
    if(shareholder[0] == ""):
      sharesAfterSplit = Decimal(shareholder[1]) * numerator / denominator
      shareholder[1] = str(sharesAfterSplit)
      newMSF.write(",".join(shareholder) + "\n")
  newMSF.close()
  return newMSF

def exportSplitNewShareTransactions(txnArr, queryAsset):
  for txns in txnArr:
    output = open("{} {} stockSplitOutputXDR.txt".format(str(datetime.now()).replace(":","."), queryAsset), "w")
    output.write(txns.to_xdr())
    output.close()

def updatePostSplitMSFbyCopyingOverRemainingShareholderInfoForBlockchainHolders(outputMSF, MSFpreSplitBalancesCSV, postSplitFileName):
  finalMSF = open(postSplitFileName, "a")
  oldMSF = open(MSFpreSplitBalancesCSV, "r")
  readData = oldMSF.read()
  readData = readData.strip()
  readData = readData.split("\n")
  oldMSF.close()
  for shareholder in readData[1:]:
    shareholder = shareholder.split(",")
    if(shareholder[0]):
      finalMSF.write(",".join(shareholder) + "\n")
  finalMSF.close()

