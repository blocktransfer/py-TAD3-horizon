import sys
sys.path.append("../")
from globals import *
import pandas

# Commission new account with voting federation address [ticker]*proxyvote.io circa sending the affidavit of notice.
# Afterwards, merge account into BT_TREASURY (single use simplifies tally logic). Remove old federation record.

CUTOFF_TIME_UTC = pandas.to_datetime("2022-07-16T10:25:00Z") # + 4hrs from ET
validAccountPublicKeys = getValidAccountPublicKeys()

def countProxyVotes(queryAsset, numVotingItems):
  votingFederationAddress = queryAsset + "*proxyvote.io"
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)
  blockchainBalancesOnRecordDate = getBalancesOnRecordDate(queryAsset)
  addrsMappedToMemos = getaddrsMappedToMemos(queryAsset, votingFederationAddress)
  balancesMappedToMemos = replaceAddressesWithRecordDateBalances(addrsMappedToMemos, blockchainBalancesOnRecordDate)
  voteTallies = parseMemosToVotes(balancesMappedToMemos, addrsMappedToMemos, numVotingItems)
  displayResults(voteTallies)

# Assume eligibility of all unrestricted outstanding shares on record date
def getNumUnrestrictedShares(queryAsset):
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

def getaddrsMappedToMemos(queryAsset, votingFederationAddress):
  addrsMappedToMemos = {}
  votingAddr = resolveFederationAddress(votingFederationAddress)
  requestAddr = getInitialAccountsRequestAddr(queryAsset)
  votingAddrData = requests.get(requestAddr).json()
  blockchainRecords = votingAddrData["_embedded"]["records"]
  numInvestorsOnboard = numInvestorsVoted = 0
  while(blockchainRecords != []):
    for everyInvestorData in blockchainRecords:
      numInvestorsOnboard += 1
      if(everyInvestorData["account_id"] in validAccountPublicKeys):
        paymentsAddrs = everyInvestorData["_links"]["payments"]["href"]
        paymentsAddrs = paymentsAddrs.replace("{?cursor,limit,order}", "?limit=" + MAX_SEARCH)
        paymentData = requests.get(paymentsAddrs).json()
        accountPaymentRecords = paymentData["_embedded"]["records"]
        while(accountPaymentRecords != []):
          for payments in accountPaymentRecords:
            try:
              if(payments["asset_type"] == "native" and payments["to"] == votingAddr and pandas.to_datetime(payments["created_at"]) < CUTOFF_TIME_UTC):
                transactionEnvelopeAddr = payments["_links"]["transaction"]["href"]
                vote = requests.get(transactionEnvelopeAddr).json()["memo"]
                addrsMappedToMemos[payments["from"]] = vote
            except KeyError:
              continue
          # Go to next payments cursor
          paymentsAddrs = paymentData["_links"]["next"]["href"].replace("\u0026", "&")
          paymentData = requests.get(paymentsAddrs).json()
          accountPaymentRecords = paymentData["_embedded"]["records"]
    # Go to next votingAddrData cursor
    requestAddr = votingAddrData["_links"]["next"]["href"].replace("\u0026", "&")
    votingAddrData = requests.get(requestAddr).json()
    blockchainRecords = votingAddrData["_embedded"]["records"]
  return addrsMappedToMemos

def replaceAddressesWithRecordDateBalances(addrsMappedToMemos, blockchainBalancesOnRecordDate):
  balancesMappedToMemos = {}
  for addresses, balances in blockchainBalancesOnRecordDate.items():
    try:
      balancesMappedToMemos[balances] = addrsMappedToMemos[addresses]
    except KeyError:
      continue
  return balancesMappedToMemos

def parseMemosToVotes(balancesMappedToMemos, addrsMappedToMemos, numVotingItems):
  delegeeAddrsMappedToSharesAllocated = {}
  delegationHashmap = makeFirst28byteMapping()
  propositionYays = [0] * numVotingItems
  propositionNays = [0] * numVotingItems
  propositionAbstains = [0] * numVotingItems
  sharesVoted = Decimal("0")
  for numShares, memos in balancesMappedToMemos.items():
    if(len(memos) > numVotingItems):
      if(memos in delegationHashmap.keys()):
        expandedAddr = delegationHashmap[memos]
        try:
          currSharesAllocated = delegeeAddrsMappedToSharesAllocated[expandedAddr]
        except KeyError:
          currSharesAllocated = 0
        totalSharesAllocated = currSharesAllocated + numShares
        delegeeAddrsMappedToSharesAllocated[expandedAddr] = totalSharesAllocated
    else:
      voteList = [votes.upper() for votes in list(memos)]
      try:
        for i, votes in enumerate(voteList):
          match votes:
            case "Y":
              propositionYays[i] += numShares
            case "N":
              propositionNays[i] += numShares
            case "A":
              propositionAbstains[i] += numShares
      except Exception:
        print("! Invalid memo: {}".format(memos))
        continue
      sharesVoted += numShares
  for delegeeAddrs, sharesAllocated in delegeeAddrsMappedToSharesAllocated.items():
    if(delegeeAddrs in validAccountPublicKeys):
      voteMemo = addrsMappedToMemos[delegeeAddrs]
      try:
        while(len(voteMemo) > numVotingItems):
          print("H")
          voteMemo = addrsMappedToMemos[voteMemo]
      except KeyError:
        sys.exit("Could not resolve voteMemo for {}".format(delegeeAddrs))
      voteList = [votes.upper() for votes in list(voteMemo)]
      try:
        for i, votes in enumerate(voteList):
          match votes:
            case "Y":
              propositionYays[i] += sharesAllocated
            case "N":
              propositionNays[i] += sharesAllocated
            case "A":
              propositionAbstains[i] += sharesAllocated
      except Exception:
        print("! Invalid memo: {}".format(memos))
        continue
      sharesVoted += sharesAllocated
  voteTallies = []
  ratio = Decimal("100")/sharesVoted
  for i in range(numVotingItems):
    yays = propositionYays[i]
    nays = propositionNays[i]
    abstains = propositionAbstains[i]
    voteTallies.append((yays, nays, abstains))
  return voteTallies

def displayResults(voteTallies):
  i = 0
  for (Y, N, A) in voteTallies:
    i += 1
    ratio = Decimal("100")/Decimal(Y+N+A)
    print("In the matter of proposition {}:".format(i))
    print("For:\t\t{}%\t({} shares)".format(format(Y*ratio, ".2f"), Y))
    print("Against:\t{}%\t({} shares)".format(format(N*ratio, ".2f"), N))
    print("Abstain:\t{}%\t({} shares)\n".format(format(A*ratio, ".2f"), A))

countProxyVotes("DEMO", 15)
