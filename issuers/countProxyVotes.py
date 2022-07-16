import sys
sys.path.append("../")
from globals import *

# Commission new account with voting federation address [ticker]*proxyvote.io circa sending the affidavit of notice.
# Afterwards, merge account into BT_TREASURY (single use simplifies tally logic). Remove old federation record.

def countProxyVotes(queryAsset, numVotingItems):
  votingFederationAddress = queryAsset + "*proxyvote.io"
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)
  blockchainBalancesOnRecordDate = getBalancesOnRecordDate(queryAsset)
  addressesMappedToMemos = getAddressesMappedToMemos(queryAsset, votingFederationAddress)
  balancesMappedToMemos = replaceAddressesWithRecordDateBalances(addressesMappedToMemos, blockchainBalancesOnRecordDate)
  voteResults = parseMemosToVotes(balancesMappedToMemos, addressesMappedToMemos, numVotingItems)
  print("---")
  print("---")
  print("---")
  print("---")
  print("---")
  print(numUnrestrictedShares)
  print("---")
  pprint(blockchainBalancesOnRecordDate)
  print("---")
  pprint(addressesMappedToMemos)
  print("---")
  pprint(balancesMappedToMemos)

  # getNumSharesEntitledToVote(...)
def getNumUnrestrictedShares(queryAsset): # TODO: change diction to numOutstandingSharesElidgibleToVote pending 8-K review
  requestAddr = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddr).json()
  try: 
    return Decimal(data["_embedded"]["records"][0]["amount"]) # Assume no voting of restricted shares
  except Exception:
    sys.exit("Input parameter error")

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

def makeFirst28byteMapping():
  delegationHashmap = {}
  inFile = open(MICR_CSV)
  MICR = inFile.read().strip().split("\n")
  inFile.close()
  for lines in MICR[1:]:
    lines = lines.split(",")
    delegationHashmap[lines[0][:28]] = lines[0]
  return delegationHashmap

def getAddressesMappedToMemos(queryAsset, votingFederationAddress):
  addressesMappedToMemos = {}
  votingAddr = resolveFederationAddress(votingFederationAddress)
  requestAddr = "https://" + HORIZON_INST + "/accounts?asset=" + queryAsset + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
  votingAddrData = requests.get(requestAddr).json()
  blockchainRecords = votingAddrData["_embedded"]["records"]
  while(blockchainRecords != []):
    for everyInvestorData in blockchainRecords:
      paymentsAddrs = everyInvestorData["_links"]["payments"]["href"]
      paymentsAddrs = paymentsAddrs.replace("{?cursor,limit,order}", "?limit=" + MAX_SEARCH)
      paymentData = requests.get(paymentsAddrs).json()
      accountPaymentRecords = paymentData["_embedded"]["records"]
      while(accountPaymentRecords != []):
        for payments in accountPaymentRecords:
          try:
            if(payments["to"] == votingAddr):
              transactionEnvelopeAddr = payments["_links"]["transaction"]["href"]
              vote = requests.get(transactionEnvelopeAddr).json()["memo"]
              addressesMappedToMemos[payments["from"]] = vote
          except KeyError:
            continue
        # Go to next payments cursor
        paymentsAddrs = paymentData["_links"]["next"]["href"].replace("\u0026", "&")
        paymentData = requests.get(paymentsAddrs).json()
        paymentRecords = paymentData["_embedded"]["records"]
    # Go to next votingAddrData cursor
    requestAddr = votingAddrData["_links"]["next"]["href"].replace("\u0026", "&")
    votingAddrData = requests.get(requestAddr).json()
    blockchainRecords = votingAddrData["_embedded"]["records"]
  return addressesMappedToMemos

def replaceAddressesWithRecordDateBalances(addressesMappedToMemos, blockchainBalancesOnRecordDate):
  balancesMappedToMemos = {}
  for addresses, balances in blockchainBalancesOnRecordDate.items():
    try:
      balancesMappedToMemos[balances] = addressesMappedToMemos[addresses]
    except KeyError:
      continue
  return balancesMappedToMemos

def parseMemosToVotes(balancesMappedToMemos, addressesMappedToMemos, numVotingItems): # this function is too big
  delegationHashmap = makeFirst28byteMapping()
  delegeesPublicKeysMappedToSharesAllocated = {}
  propositionYays = propositionNays = propositionAbstains = [0] * numVotingItems
  numSharesVoted = 1  # 0
  # initial count & collect any delegation instructions
  for numShares, memos in balancesMappedToMemos.items():
    if(len(memos) > numVotingItems):
      if(memos in delegationHashmap.keys()):
        delegeesPublicKeysMappedToSharesAllocated[delegationHashmap[memos]] += numShares
        # numSharesVoted += numShares
    else:
      numSharesVoted += numShares
      voteList = [votes.upper() for votes in list(memos)]
      try:
        for i, votes in enumerate(voteList):
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
  # delegation instructions -> memo
  # then adjust counts based on parse
  pprint(delegeesPublicKeysMappedToSharesAllocated)
  for delegees, sharesAllocated in delegeesPublicKeysMappedToSharesAllocated.items():
    # addressesMappedToMemos[delegees] ...
    if(sharesAllocated):
      sys.exit("todo: DELEGATION FUNCTIONALITY REQUIRED")
    # edge test if a delegee delegates to another delegee (requires internal looping)
  voteResults = []
  numSharesVoted = Decimal(numSharesVoted)
  for i in range(numVotingItems):
    yays = propositionYays[i]
    nays = propositionNays[i]
    abstains = propositionAbstains[i]
    voteResults.append((yays, nays, abstains))
    ratio = Decimal("100")/numSharesVoted
    voteResults.append((format(yays*ratio, ".2f"), format(nays*ratio, ".2f"), format(abstains*ratio, ".2f")))
    
  return voteResults

countProxyVotes("DEMO", 7)
