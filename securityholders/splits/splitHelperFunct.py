from datetime import datetime

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

