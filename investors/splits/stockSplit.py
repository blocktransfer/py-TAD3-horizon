import sys
sys.path.append("../../")
from globals import *

# In general:
#   num > denom:
#     forward split
#     new shares from distributor
#   else:
#     reverse split
#     clackback from issuer
# Freeze accounts during execution

def stockSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesTXT, recordDate):
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  ratio = numerator / denominator
  reason = f"{numerator}-for-{denominator} split ({recordDate})"
  offlineRoundingDiff = generatePostSplitMSF(MSFpreSplitBalancesTXT, ratio)
  adjTransactionsArray, ledgerRoundingDiff = getSplitTxnsArrToAdjustLedger(queryAsset, ratio, reason)
  exportSplitTransactions(adjTransactionsArray, queryAsset)
  totalRecordDifference = offlineRoundingDiff + ledgerRoundingDiff
  print(f"""\n***\nRecord Differences:\n
  \tOffline: {str(offlineRoundingDiff)} {queryAsset}\n
  \tLedger: {str(ledgerRoundingDiff)} {queryAsset}\n
  \tTotal: {str(totalRecordDifference)} {queryAsset}\n
  ***\n""")

def generatePostSplitMSF(MSFpreSplitBalancesTXT, ratio):
  if(ratio > 1):
    postSplitFileName = f"[FORWARD] {queryAsset} Post-Split Master Securityholder File.txt"
  else:
    postSplitFileName = f"[REVERSE] {queryAsset} Post-Split Master Securityholder File.txt"
  with open(MSFpreSplitBalancesTXT) as oldMSF:
    with open(f"/outputs/{postSplitFileName}", "w") as newMSF:
      newMSF.write(f"{next(oldMSF)}\n")
      recordDifference = Decimal("0")
      for accounts in oldMSF:
        account = accounts.split("|")
        offlineShares = Decimal(account[1])
        if(offlineShares):
          roundedValue = roundUp(offlineShares * ratio)
          recordDifference += roundedValue - offlineShares
          account[1] = str(roundedValue)
        newMSF.write(f"{'|'.join(account)}")
  return recordDifference

def roundUp(numShares):
  return numShares.quantize(MAX_PREC, rounding = "ROUND_UP")

def getSplitTxnsArrToAdjustLedger(queryAsset, ratio, reason):
  balanceAdjTransactionsArray, diffB = getBalanceAdjustments(queryAsset, ratio)
  CBtransactionsArray, diffCB = getClaimableBalanceAdjustments(queryAsset, ratio)
  combinedTxnArr = balanceAdjTransactionsArray.append(CBtransactionsArray)
  totalLedgerRecordDifference = diffB + diffCB
  return combinedTxnArr, totalLedgerRecordDifference

def getBalanceAdjustments(queryAsset, ratio):
  transactions = []
  numTxnOps = idx = 0
  source = getSource(ratio)
  recordDifference = Decimal("0")
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  for addresses, balances in getLedgerBalances(queryAsset).items():
    sharesToClawback = balances - (balances * ratio)
    if(sharesToClawback):
      rounded = roundUp(sharesToClawback)
      recordDifference += rounded - sharesToClawback
      transactions[idx].append_clawback_op(
        asset = Asset(queryAsset, BT_ISSUER),
        from_ = addresses,
        amount = rounded,
      )
      numTxnOps += 1
    if(checkLimit(numTxnOps)):
      idx, numTxnOps = renew(transactions, source, idx)
  return prepAndSignForOutput(transactions, reason)

def getClaimableBalanceAdjustments(transactions, stats):
  transactions = []
  numTxnOps = idx = 0
  source = getSource(ratio)
  recordDifference = Decimal("0")
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  for balanceIDs, data in getClaimableBalancesData(queryAsset).items():
    transactions[idx].append_clawback_claimable_balance_op(
      balance_id = balanceIDs
    )
    newNumRestrictedShares = data["amount"] * ratio
    rounded = roundUp(newNumRestrictedShares)
    recordDifference += rounded - newNumRestrictedShares
    transactions[idx].append_create_claimable_balance_op(
      asset = Asset(queryAsset, BT_ISSUER),
      amount = rounded,
      claimants = [
        Claimant(
          destination = data["recipient"],
          predicate = ClaimPredicate.predicate_not(
            ClaimPredicate.predicate_before_relative_time(data["release"])
          )
        )
      ]
    )
    numTxnOps += 2
    if(checkLimit(numTxnOps)):
      idx, numTxnOps = renew(transactions, ratio, idx)
  return prepAndSignForOutput(transactions, reason)

def getSource(ratio):
  if(ratio > 1):
    return distributor
  else:
    return issuer

def renew(transactions, source, idx):
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  return idx + 1, 0

def prepAndSignForOutput(transactionsArray, reason):
  builtTransactions = []
  for txns in transactionsArray:
    builtTransactions.append(prep(txns, reason))
  for txns in builtTransactions:
    txns.sign(Keypair.from_secret(ISSUER_KEY))
  return output

def exportSplitTransactions(transactionsArray, queryAsset):
  for txns in transactionsArray:
    now = str(datetime.now()).replace(":",".")
    with open(f"/outputs/{now} {queryAsset} StockSplitOutputXDR.txt", "w") as output:
      output.write(txns.to_xdr())

reverseSplit("DEMO", 1, 10, "preSplitVeryRealStockIncMSF.txt", "2022-1-18")