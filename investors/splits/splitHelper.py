import sys
sys.path.append("../../")
from globals import *

def getClaimableBalancesData(queryAsset):
  claimableBalanceIDsMappedToData = {}
  data = {}
  b = []
  requestAddr = f"{HORIZON_INST}/claimable_balances?asset={queryAsset}:{BT_ISSUER}&{MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for claimableBalances in ledger["_embedded"]["records"]:
      b.append(str(claimableBalances))
      data["release"] = 0
      for claimants in claimableBalances["claimants"]:
        try:
          data["release"] = claimants["predicate"]["not"]["abs_before_epoch"]
        except KeyError:
          continue # Expect investor as claimant via not abs_before
      if(data["release"]):
        data["recipient"] = claimants["destination"]
        # data["amount"] = Decimal(claimableBalances["amount"])
        data["amount"] = claimableBalances["amount"]
        claimableBalanceIDsMappedToData[claimableBalances["id"]] = data
    ledger = getNextLedgerData(ledger)
  return claimableBalanceIDsMappedToData, b

def roundUp(numShares):
  return numShares.quantize(MAX_PREC, rounding=ROUND_UP)

def prep(transaction, reason):
  return transaction.add_text_memo(reason).set_timeout(7200).build()

def checkLimit(numTxnOps):
  match numTxnOps:
    case 1:
      return numTxnOps >= MAX_NUM_TXN_OPS
    case 2:
      return numTxnOps >= MAX_NUM_TXN_OPS - 1

def renew(transactions, source, idx):
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  idx += 1
  return idx, 0

def displayDifference(difference):
  print(f"\n***\ntotalRecordDifference: {str(difference)}\n***\n")

def generatePostSplitMSF(MSFpreSplitBalancesTXT, ratio, postSplitFileName):
  oldMSF = open(MSFpreSplitBalancesTXT)
  newMSF = open(postSplitFileName, "w")
  newMSF.write(next(oldMSF) + "\n")
  totalRoundingRecordDifference = 0
  for accounts in oldMSF:
    account = accounts.split("|")
    if(account[1]):
      roundedValue = Decimal(account[1]) * ratio
      account[1] = roundedValue.quantize(MAX_PREC, rounding = ROUND_UP)
      difference = abs(roundedValue - sharesToClawback)
      totalRoundingRecordDifference += difference
      if(difference):
        print(f"Rounded up for {account[2]}: {difference} shares")
      newMSF.write(f"{'|'.join(account)}")
    else:
      newMSF.write(f"{'|'.join(account)}")
  print(f"\nRounded up {totalRoundingRecordDifference} total shares")
  oldMSF.close()
  newMSF.close()
  return newMSF

def exportSplitNewShareTransactions(txnArr, queryAsset):
  for txns in txnArr:
    output = open(f"{str(datetime.now()).replace(':','.')} {queryAsset} StockSplitOutputXDR.txt", "w")
    output.write(txns.to_xdr())
    output.close()

