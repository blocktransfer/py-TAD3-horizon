import sys
sys.path.append("../")
from globals import *

# Commission NEW account with voting federation address [ticker]*proxyvote.io circa sending the affidavit of notice.
# Afterwards, merge account into BT_TREASURY (single use simplifies tally logic). Remove old federation record.

def countProxyVotes(queryAsset, numVotingItems):
  votingFederationAddress = queryAsset + "*proxyvote.io"
  recordDateInvestorBalancesCSV = queryAsset + " Record Date List.csv"
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)
  blockchainBalancesOnRecordDate = getBalancesOnRecordDate()

def getNumUnrestrictedShares(queryAsset): # TODO: change diction to numOutstandingSharesElidgibleToVote per 8-K review
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddress).json()
  return Decimal(data["_embedded"]["records"][0]["amount"]) # Assume no voting of restricted shares

def getBalancesOnRecordDate(queryAsset):
  balancesOnRecordDate = {}
  
  internalRecordDateCSV = G_DIR + "/../../pii/" + datetime.today().year + "/internal-record-date-snapshots/" + queryAsset + ".csv"
  
  inFile = open(internalRecordDateCSV)
  internalRecordDateHoldings = inFile.read().strip().split("\n")
  inFile.close()
  for lines in internalRecordDateHoldings:
    balancesOnRecordDate[lines[0]] = lines[1]
  
  return balancesOnRecordDate

countProxyVotes("DEMO", 7)