import sys
sys.path.append("../")
from globals import *

# Commission NEW account with voting federation address [ticker]*proxyvote.io circa sending the affidavit of notice.
# Afterwards, merge account into BT_TREASURY (single use simplifies tally logic). Remove old federation record.

def countProxyVotes(queryAsset, numVotingItems):
  votingFederationAddress = queryAsset + "*proxyvote.io"
  recordDateInvestorBalancesCSV = queryAsset + " Draft Record Date List.csv"
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)

def getNumUnrestrictedShares(queryAsset):
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddress).json()
  return Decimal(data["_embedded"]["records"][0]["amount"]) # Assume no voting of restricted shares

def mergeBlockchainRecordsWithMSF(queryAsset, MSF, totalOutstandingShares, StellarBlockchainBalances):
  inFile = open(MSF)
  readFile = inFile.read().strip().split("\n")
  inFile.close()
  mergedMSF = open("{} Master Securityholder File as of {}.csv".format(queryAsset, datetime.now().strftime("%Y-%m-%d at %H%MZ")), "w")
  mergedMSF.write("Shares,Percent of Outstanding Shares,Registration,Email,Date of Birth / Organization,Address,Address Extra,City,State,Postal Code,Country,Onboarded Date,Issue Date of Security,Cancellation Date of Security,Dividends,Restricted Shares Notes\n")
  for lines in readFile[1:]:
    lines = lines.split(",")
    sharesNotYetClaimedOnStellar = 0 if lines[1] == "" else Decimal(lines[1])
    try:
        blockchainBalance = 0 if lines[0] == "" else StellarBlockchainBalances[lines[0]]
    except KeyError:
        print("{} is no longer a securityholder per removed trustline. Prune from merged MSF".format(lines[0]))
        continue
    totalBalance = blockchainBalance + sharesNotYetClaimedOnStellar # Redundant given restricted entries are separate from unrestricted entries 
    lines[0] = str(totalBalance)
    lines[1] = str(totalBalance / totalOutstandingShares)
    mergedMSF.write(",".join(lines) + "\n")
  mergedMSF.close()

countProxyVotes("DEMO", 7)