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
  addressesMappedToMemos = getAddressesMappedToMemos(queryAsset, votingFederationAddress)
  balancesMappedToMemos = replaceAddressesWithRecordDateBalances(addressesMappedToMemos, blockchainBalancesOnRecordDate)
  voteResults = parseMemosToVotes(balancesMappedToMemos, numVotingItems)
  
  print(numUnrestrictedShares)
  print("---")
  pprint(blockchainBalancesOnRecordDate)
  print("---")
  pprint(addressesMappedToMemos)
  print("---")
  pprint(balancesMappedToMemos)

def getNumUnrestrictedShares(queryAsset): # TODO: change diction to numOutstandingSharesElidgibleToVote pending 8-K review
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
    SHA256ofPublicKey = hashlib.sha256(lines[0].encode()).hexdigest()
    delegationHashmap[SHA256ofPublicKey] = lines[0]
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

def replaceAddressesWithRecordDateBalances(addressesMappedToMemos, blockchainBalancesOnRecordDate):
  balancesMappedToMemos = {}
  for addresses, balances in blockchainBalancesOnRecordDate.items():
    try:
      balancesMappedToMemos[balances] = addressesMappedToMemos[addresses]
    except KeyError:
      continue
  return balancesMappedToMemos

def parseMemosToVotes(balancesMappedToMemos, numVotingItems):
  delegationHashmap = makeHashmapForDelegation()
  delegeesPublicKeysMappedToSharesAllocated = {}
  propositionYays = propositionNays = propositionAbstains = [0] * numVotingItems
  numSharesVoted = 0
  for numShares, memos in balancesMappedToMemos:
    if(len(memo) > numVotingItems):
      if(memo in delegationHashmap.keys()):
        delegeesPublicKeysMappedToSharesAllocated[delegationHashmap[memo]] += numShares
        # numSharesVoted += numShares
    else:
      numSharesVoted += numShares
      voteList = [votes.upper() for votes in list(memo)]
      try:
        for i, votes in enumerate(voteList()):
          match status:
            case "Y":
              propositionYays[i] += numShares
            case "N":
              propositionNays[i] += numShares
            case "A":
              propositionAbstains[i] += numShares
            ###
      except Exception:
        print("Debug: Exception on vote parser with memo {}".format(memo))
        continue
  for delegees, sharesAllocated in delegeesPublicKeysMappedToSharesAllocated.items():
    if(sharesAllocated):
      sys.exit("todo: DELEGATION FUNCTIONALITY REQUIRED")
  voteResults = []
  numSharesVoted = Decimal(numSharesVoted)
  oneH = Decimal(100)
  for i in range(numVotingItems):
    yays = propositionYays[i]
    nays = propositionNays[i]
    abstains = propositionAbstains[i]
    voteResults.append((yays, nays, abstains))
    voteResults.append((oneH*Decimal(yays)/numSharesVoted, oneH*Decimal(nays)/numSharesVoted, oneH*Decimal(abstains)/numSharesVoted))
    
  return voteResults

countProxyVotes("StellarMart", 7)