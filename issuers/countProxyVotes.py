import sys
sys.path.append("../")
from globals import *
import hashlib

# Commission NEW account with voting federation address [ticker]*proxyvote.io circa sending the affidavit of notice.
# Afterwards, merge account into BT_TREASURY (single use simplifies tally logic). Remove old federation record.

def countProxyVotes(queryAsset, numVotingItems):
  votingFederationAddress = queryAsset + "*proxyvote.io"
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)
  blockchainBalancesOnRecordDate = getBalancesOnRecordDate(queryAsset)
  delegationHashmap = makeHashmapForDelegation()
  addressesMappedToMemos = getAddressesMappedToMemos(queryAsset, votingFederationAddress)
  balancesMappedToMemos = replaceAddressesWithRecordDateBalances(queryAsset, recordDateInvestorBalancesCSV)
  

def getNumUnrestrictedShares(queryAsset): # TODO: change diction to numOutstandingSharesElidgibleToVote per 8-K review
  requestAddr = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddr).json()
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

def getAddressesMappedToMemos(queryAsset, votingFederationAddress):
  addressesMappedToMemos = {}
  votingAddr = resolveFederationAddress(votingFederationAddress)
  # get all txns inbound to address
  requestAddr = "https://" + HORIZON_INST + "/accounts?asset=" + queryAsset + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
  votingAddrData = requests.get(requestAddr).json()
  paymentsAddr = votingAddrData["_embedded"]["records"][0]["_links"]["payments"]["href"]
  paymentsAddr = paymentsAddr.replace("{?cursor,limit,order}", "?limit=" + MAX_SEARCH)
  paymentData = requests.get(paymentsAddr).json()
  paymentRecords = paymentData["_embedded"]["records"]
  while(paymentRecords != []):
    for payments in paymentRecords:
      try:
        if(payments["to"] == votingAddr):
          transactionEnvelopeAddr = payments["_links"]["transaction"]["href"]
          vote = requests.get(transactionEnvelopeAddr).json()["memo"]
          addressesMappedToMemos[payments["from"]] = vote
      except KeyError:
        continue
    # Go to next cursor
    paymentsAddr = paymentData["_links"]["next"]["href"].replace("\u0026", "&")
    paymentData = requests.get(paymentsAddr).json()
    paymentRecords = paymentData["_embedded"]["records"]
  return addressesMappedToMemos

#queryAssetOnStellar = Asset(queryAsset, BT_ISSUER)
countProxyVotes("StellarMart", 7)