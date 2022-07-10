import sys
sys.path.append("../")
from globals import *
import hashlib

# Commission NEW account with voting federation address [ticker]*proxyvote.io circa sending the affidavit of notice.
# Afterwards, merge account into BT_TREASURY (single use simplifies tally logic). Remove old federation record.

def countProxyVotes(queryAsset, numVotingItems):
  votingFederationAddress = queryAsset + "*proxyvote.io"
  recordDateInvestorBalancesCSV = queryAsset + " Record Date List.csv"
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)
  blockchainBalancesOnRecordDate = getBalancesOnRecordDate(queryAsset)
  delegationHashmap = makeHashmapForDelegation()
  addressesMappedToVoteMemos = getAddressesMappedToVotes(queryAsset, votingFederationAddress)
  

def getNumUnrestrictedShares(queryAsset): # TODO: change diction to numOutstandingSharesElidgibleToVote per 8-K review
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddress).json()
  return Decimal(data["_embedded"]["records"][0]["amount"]) # Assume no voting of restricted shares

def getBalancesOnRecordDate(queryAsset):
  balancesOnRecordDate = {}
  internalRecordDateCSV = G_DIR + "/../../pii/internal-record-date-snapshots/" + str(datetime.today().year) + "/" + queryAsset + ".csv"
  inFile = open(internalRecordDateCSV)
  internalRecordDateHoldings = inFile.read().strip().split("\n")
  inFile.close()
  for lines in internalRecordDateHoldings[1:]:
    lines = lines.split(",")
    balancesOnRecordDate[lines[0]] = Decimal(lines[1])
  return balancesOnRecordDate

def makeHashmapForDelegation():
  delegationHashmap = {}
  inFile = open(MICR_CSV)
  MICR = inFile.read().strip().split("\n")
  inFile.close()
  for lines in MICR[1:]:
    lines = lines.split(",")
    SHA256ofPublicKey = hashlib.sha256(lines[0].encode())
    delegationHashmap[SHA256ofPublicKey.hexdigest()] = lines[0]
  return delegationHashmap

def getAddressesMappedToVotes(queryAsset, votingFederationAddress):
  votingAddr = resolveFederationAddress(votingFederationAddress)
  # get all txns inbound to address
  requestAddress = "https://" + HORIZON_INST + "/accounts?asset=" + queryAsset + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
  data = requests.get(requestAddress).json()
  blockchainRecords = data["_embedded"]["records"]["transactions"]
  
  print(blockchainRecords)
  # parse source
  
  queryAssetOnStellar = Asset(queryAsset, BT_ISSUER)
  # parse memo

countProxyVotes("StellarMart", 7)