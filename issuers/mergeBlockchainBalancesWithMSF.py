import sys
sys.path.append("../")
from globals import *

# testing: getMergedReportForAssetWithNumRestrictedSharesUsingMSF("StellarMart", 10000, "VeryRealStockIncMSF.csv")
def getMergedReportForAssetWithNumRestrictedSharesUsingMSF(queryAsset, numRestrictedShares, MSF):
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares)
  mergeBlockchainRecordsWithMSF(queryAsset, MSF, totalOutstandingShares, StellarBlockchainBalances)

def getTotalOutstandingShares(queryAsset, numRestrictedShares):
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddress).json()
  numUnrestrictedShares = Decimal(data["_embedded"]["records"][0]["amount"])
  totalOutstandingShares = numRestrictedShares + numUnrestrictedShares
  return totalOutstandingShares

def mergeBlockchainRecordsWithMSF(queryAsset, MSF, totalOutstandingShares, StellarBlockchainBalances):
  inFile = open(MSF)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split("\n")
  inFile.close()
  mergedMSF = open("{} Master Securityholder File as of {}.csv".format(queryAsset, datetime.now().strftime("%Y-%m-%d at %H%MZ")), "w")
  mergedMSF.write("Shares,Percent of Outstanding Shares,Registration,Email,Date of Birth / Organization,Address,Address Extra,City,State,Postal Code,Country,Onboarded Date,Issue Date of Security,Cancellation Date of Security,Dividends,Restricted Shares Notes\n")
  for lines in readFile[1:]:
    lines = lines.split(",")
    sharesNotYetClaimedOnStellar = 0 if lines[1] == "" else Decimal(lines[1])
    try:
        blockchainBalance = 0 if lines[0] == "" else StellarBlockchainBalances[lines[0]]
    except KeyError:
        # This address is no longer a securityholder per removed trustline. Prune from merged MSF
        continue
    totalBalance = blockchainBalance + sharesNotYetClaimedOnStellar # Redundant given restricted entries are separate from unrestricted entries 
    lines[0] = str(totalBalance)
    lines[1] = str(totalBalance / totalOutstandingShares)
    mergedMSF.write(",".join(lines) + "\n")
  mergedMSF.close()
  