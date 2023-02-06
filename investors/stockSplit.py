import sys
sys.path.append("../")
from globals import *

# testing: stockSplit("StellarMart", 1, 10, "preSplitVeryRealStockIncMSF.txt", "2022-1-18")
def stockSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesTXT, recordDate):
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  ratio = numerator / denominator
  reason = f"{numerator}-for-{denominator} split ({recordDate})"
  offlineRoundingUpDiff = generatePostSplitMSF(queryAsset, ratio, MSFpreSplitBalancesTXT)
  adjustmentTransactionsArray, ledgerRoundingUpDiff = getTransactionsArrayToEffectSplit(queryAsset, ratio, reason)
  exportSplitTransactions(queryAsset, adjustmentTransactionsArray)
  totalRecordDifference = offlineRoundingUpDiff + ledgerRoundingUpDiff
  # update docs/assets/[[CURRENCIES]]/splits inline tables
  print(f"""\n  Record Differences:\n
  \tOffline: {str(offlineRoundingUpDiff if offlineRoundingUpDiff else 0)} {queryAsset}\n
  \tLedger: {str(ledgerRoundingUpDiff)} {queryAsset}\n
  \tTotal: {str(totalRecordDifference)} {queryAsset}\n\n""")

def generatePostSplitMSF(queryAsset, ratio, MSFpreSplitBalancesTXT):
  if(ratio > 1):
    postSplitFileName = f"[FORWARD] {queryAsset} Post-Split Master Securityholder File.txt"
  else:
    postSplitFileName = f"[REVERSE] {queryAsset} Post-Split Master Securityholder File.txt"
  with open(MSFpreSplitBalancesTXT) as oldMSF:
    with open(f"{G_DIR}/outputs/{postSplitFileName}", "w") as newMSF:
      newMSF.write(f"{next(oldMSF)}\n")
      recordDifference = Decimal("0")
      for accounts in oldMSF:
        account = accounts.split("|")
        if(account[1]):
          adjustedOfflineShares = Decimal(account[1]) * ratio
          roundedValue = roundUp(adjustedOfflineShares)
          recordDifference += roundedValue - adjustedOfflineShares
          account[1] = str(roundedValue).replace(".0000000", "")
        newMSF.write("|".join(account))
  return recordDifference

def roundUp(numShares):
  return numShares.quantize(MAX_PREC, rounding = "ROUND_UP")

def getTransactionsArrayToEffectSplit(queryAsset, ratio, reason):
  balanceAdjTransactionsArray, diffB = getBalanceAdjustments(queryAsset, ratio, reason)
  CBtransactionsArray, diffCB = getClaimableBalanceAdjustments(queryAsset, ratio, reason)
  return balanceAdjTransactionsArray + CBtransactionsArray, diffB + diffCB

def getBalanceAdjustments(queryAsset, ratio, reason):
  transactions = []
  numTxnOps = i = 0
  source = getSource(ratio, queryAsset)
  roundingUpDifference = Decimal("0")
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  for addresses, balances in getLedgerBalances(queryAsset).items():
    adjustedBalance = getBalAdjAmount(balances, ratio)
    rounded = roundUp(adjustedBalance)
    roundingUpDifference += rounded - adjustedBalance
    if(ratio > 1):
      transactions[i].append_payment_op(
        destination = addresses,
        asset = getAssetObjFromCode(queryAsset),
        amount = rounded,
      )
    else:
      transactions[i].append_clawback_op(
        asset = getAssetObjFromCode(queryAsset),
        from_ = addresses,
        amount = rounded,
      )
    numTxnOps += 1
    if(checkLimit(numTxnOps)):
      i, numTxnOps = renew(transactions, source, i)
  return prepAndSignForOutput(transactions, reason), roundingUpDifference

def getBalAdjAmount(balances, ratio):
  if(ratio > 1):
    return (balances * ratio) - balances
  else:
    return balances - (balances * ratio)

def getClaimableBalanceAdjustments(queryAsset, ratio, reason):
  transactions = []
  numTxnOps = i = 0
  source = getSource(ratio, queryAsset)
  roundingUpDifference = Decimal("0")
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  for balanceIDs, data in getClaimableBalancesData(queryAsset).items():
    adjustedAmount = data["amount"] * ratio
    rounded = roundUp(adjustedAmount)
    roundingUpDifference += rounded - adjustedAmount
    transactions[i].append_clawback_claimable_balance_op(
      balance_id = balanceIDs
    )
    transactions[i].append_create_claimable_balance_op(
      asset = getAssetObjFromCode(queryAsset),
      amount = rounded,
      claimants = [
        Claimant(
          destination = data["recipient"],
          predicate = ClaimPredicate.predicate_not(
            ClaimPredicate.predicate_before_absolute_time(data["release"])
          )
        )
      ]
    )
    numTxnOps += 2
    if(checkLimit(numTxnOps)):
      i, numTxnOps = renew(transactions, source, i)
  return prepAndSignForOutput(transactions, reason), roundingUpDifference

def getSource(ratio, queryAsset):
  if(ratio > 1):
    return distributor
  else:
    return getIssuerAccObj(queryAsset)

def checkLimit(numTxnOps):
  return numTxnOps >= MAX_NUM_TXN_OPS

def prep(transaction, reason):
  return transaction.add_text_memo(reason).set_timeout(7200).build()

def renew(transactions, source, i):
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  return i + 1, 0

def prepAndSignForOutput(transactionsArray, reason):
  builtTransactions = []
  for txns in transactionsArray:
    builtTransactions.append(prep(txns, reason))
  for txns in builtTransactions:
    txns.sign(Keypair.from_secret(ISSUER_KEY))
  return builtTransactions

def getClaimableBalancesData(queryAsset):
  claimableBalanceIDsMappedToData = {}
  issuer = getAssetIssuer(queryAsset)
  requestAddr = f"{HORIZON_INST}/claimable_balances?asset={queryAsset}:{issuer}&{MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for claimableBalances in ledger["_embedded"]["records"]:
      data = {"release": 0}
      for claimants in claimableBalances["claimants"]:
        try:
          data["release"] = int(claimants["predicate"]["not"]["abs_before_epoch"])
          break
        except KeyError:
          continue # Expect investor as claimant via not abs_before
      if(data["release"]):
        data["recipient"] = claimants["destination"]
        data["amount"] = Decimal(claimableBalances["amount"])
        claimableBalanceIDsMappedToData[claimableBalances["id"]] = data
    ledger = getNextLedgerData(ledger)
  return claimableBalanceIDsMappedToData

def exportSplitTransactions(queryAsset, transactionsArray):
  for txns in transactionsArray:
    now = str(datetime.now()).replace(":",".")
    with open(f"{G_DIR}/outputs/{now} {queryAsset} StockSplitOutputXDR.txt", "w") as output:
      output.write(txns.to_xdr())

