import sys
sys.path.append("../")
from globals import *

# Record dates at midnight UTC

# have client terms include:
#   approval of digital proxy
#   them-indenmity of cost basis reporting; escheatment
#   us-indenmity of broker search per 14a-13
#     meeting notice 10-60 days prior
#     via Broadridge: search requests to intermediaries for mailing counts rip,
#     20 days prior to Record Date
#   Information you migth need:
#     Block Transfer
#     www.blocktransfer.io
#     99 Wall Street #4640
#     New York, NY 10005
#     Email: support@blocktransfer.io
#     Call or Text: (844) 42-STOCK
#     [Internal] proxy.announcements@blocktransfer.io
#     [Internal] issuer.support@blocktransfer.io
#  Limitation of Liability (for a Stock Transfer Agent)
#  Support transfer agents in their common practice of limiting their own liability on wayward stock transfers to the amount of fees the corporate client paid the agent in the preceding 12 months.
#  Dividend Payments
#  Should the Company pay dividends , ... Transfer agents can require the company to fund 100% of the  dividend money on mail date, or 100% on payable date, or a hybrid arrangement  where, say, funding of checks and electronic credit advices happens on mail  date, and funding of the remainder (mostly for institutional investors owning  through the Depository Trust Company) takes place on payable date
#  Mail date is when dividend checks and advices  of electronic dividend payment are mailed by the transfer agent.    Payable date is when dividend payment by the company officially happens.

# Comprehensive meeting checklist (todo: auto calendar events -> CRM?):
# T-64  Request text for message box in email template
# T-60  Record date
# T-59  Share record-date list; request combined digital annual report and 10K/digital proxy statement and card [portal to upload to?]
# T-55  Upload docs and establish proper web addresses incl. federation
# T-54  Submit postgrid campaign (5-10 biz days for delivery, including 2-day processing)
# T-47  Send emails
# T-46  Submit new postgrid campaign for undeliverable emails
# T-43  Send signed affidavit of notice 
# T-15  Send preliminary vote results
# T-1   Send day-prior vote results
# T     Send final vote results

# (shareable tabulating widget - simple executable GUI?)
# Last day reasonable for mailing materisl T-9?

VOTE_CUTOFF_TIME_UTC = pandas.to_datetime("2031-04-29T12:30:00Z") # set to meeting time for audits
validAccountPublicKeys = getValidAccountPublicKeys()

#testing: countProxyVotes("DEMO", 15, "annual")
def countProxyVotes(queryAsset, numVotingItems, meetingType):
  votingFederationAddress = f"{queryAsset}-{meetingType}-{datetime.today().year}*proxyvote.io" # +1 for year-end meeting
  numUnrestrictedShares = getNumUnrestrictedShares(queryAsset)
  blockchainBalancesOnRecordDate = getBalancesOnRecordDate(queryAsset)
  addrsMappedToMemos = getaddrsMappedToMemos(queryAsset, votingFederationAddress)
  balancesMappedToMemos = replaceAddressesWithRecordDateBalances(addrsMappedToMemos, blockchainBalancesOnRecordDate)
  voteTallies = parseMemosToVotes(balancesMappedToMemos, addrsMappedToMemos, numVotingItems)
  displayResults(queryAsset, voteTallies)

# Assume eligibility of all unrestricted outstanding shares on record date
def getNumUnrestrictedShares(queryAsset):
  requestAddr = f"https://{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  data = requests.get(requestAddr).json()
  try: 
    return Decimal(data["_embedded"]["records"][0]["amount"]) # Assume no voting of restricted shares
  except Exception:
    sys.exit("Input parameter error")

def getBalancesOnRecordDate(queryAsset):
  balancesOnRecordDate = {}
  internalRecordDateCSV = f"{G_DIR}/../pii/internal-record-date-snapshots/{str(datetime.today().year)}/{queryAsset}.csv"
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
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  numInvestorsOnboard = numInvestorsVoted = 0
  while(blockchainRecords != []):
    for everyInvestorData in blockchainRecords:
      numInvestorsOnboard += 1
      if(everyInvestorData["account_id"] in validAccountPublicKeys):
        paymentsAddrs = everyInvestorData["_links"]["payments"]["href"].replace("{?cursor,limit,order}", f"?limit={MAX_SEARCH}")
        paymentData = requests.get(paymentsAddrs).json()
        accountPaymentRecords = paymentData["_embedded"]["records"]
        while(accountPaymentRecords != []):
          for payments in accountPaymentRecords:
            try:
              if(payments["asset_type"] == "native" and payments["to"] == votingAddr and pandas.to_datetime(payments["created_at"]) < VOTE_CUTOFF_TIME_UTC):
                transactionEnvelopeAddr = payments["_links"]["transaction"]["href"]
                vote = requests.get(transactionEnvelopeAddr).json()["memo"]
                addrsMappedToMemos[payments["from"]] = vote
            except KeyError:
              continue
          accountPaymentRecords, paymentData = getNextCursorRecords(paymentData)
    blockchainRecords, data = getNextCursorRecords(data)
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
  #pprint(addrsMappedToMemos)
  #print(balancesMappedToMemos) 
  delegeeAddrsMappedToSharesAllocated = {}
  delegationHashmap = makeFirst28byteMapping()
  propositionYays = [0] * numVotingItems
  propositionNays = [0] * numVotingItems
  propositionAbstains = [0] * numVotingItems
  propositionWitholds = [0] * numVotingItems
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
            case "W":
              propositionWitholds[i] += numShares
      except Exception:
        print("! Invalid memo: {}".format(memos))
        continue
      sharesVoted += numShares
  # todo: segment both these two sections into their own functions
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
            case "W":
              propositionWitholds[i] += sharesAllocated
      except Exception:
        print("! Invalid memo: {}".format(memos))
        continue
      sharesVoted += sharesAllocated
  voteTallies = []
  ratio = Decimal("100") / sharesVoted
  for i in range(numVotingItems):
    yays = propositionYays[i]
    nays = propositionNays[i]
    abstains = propositionAbstains[i]
    witholds = propositionWitholds[i]
    voteTallies.append(
      (
        yays,
        nays,
        abstains,
        witholds
      )
    )
  return voteTallies

def displayResults(queryAsset, voteTallies):
  outstanding = getStockOutstandingShares(queryAsset)
  i = 0
  for (Y, N, A, W) in voteTallies:
    i += 1
    ratio = Decimal("100") / Decimal(Y + N + A + W)
    ratioTot = Decimal("100") / outstanding
    print("In the matter of proposition {}:".format(i))
    print("For:\t\t{}%\t({} shares)".format(
        f"{Y * ratio}:.2f",
        f"{Y * ratioTot}:.2f",
        Y
      )
    ) # todo: test, finalize export functionality as master tab.
    print("Against:\t{}%\t({} shares)".format(format(N * ratio, ".2f"), N))
    print("Abstain:\t{}%\t({} shares)\n".format(format(A * ratio, ".2f"), A))
    print("Withold:\t{}%\t({} shares)\n".format(format(W * ratio, ".2f"), W))

