from splitHelper import *

# testing: forwardSplit("StellarMart", 5, 2, "preSplitVeryRealStockIncMSF.txt", "2022-1-18")
def forwardSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesTXT, recordDate):
  postSplitFileName = f"[FORWARD] {queryAsset} Post-Split Master Securityholder File.txt"
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator > denominator 
  ledgerBalances = getLedgerBalances(queryAsset)
  newShareTxnArr = grantNewSplitSharesFromBalancesClaimedOnStellar(ledgerBalances, queryAsset, numerator, denominator, recordDate)
  exportSplitNewShareTransactions(newShareTxnArr, queryAsset)
  generatePostSplitMSF(MSFpreSplitBalancesTXT, numerator / denominator, postSplitFileName)

def grantNewSplitSharesFromBalancesClaimedOnStellar(ledgerBalances, queryAsset, numerator, denominator, recordDate):
  transactions = []
  ratio = numerator / denominator
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, distributor)
  reason = f"{numerator}-for-{denominator} split ({recordDate})"
  numTxnOps = idx = 0
  for addresses, balances in ledgerBalances.items():
    sharesToPay = (balances * ratio) - balances
    if(sharesToPay):
      rounded = roundUp(sharesToPay)
      recordDifference += rounded - sharesToPay
      transactions[idx].append_payment_op(
        destination = addresses,
        asset = Asset(queryAsset, BT_ISSUER),
        amount = rounded,
      )
      numTxnOps += 1
    if(checkLimit(numTxnOps)):
      transactions[idx] = prep(transactions[idx], reason)
      transactions[idx].sign(Keypair.from_secret(DISTRIBUTOR_KEY))
      idx, numTxnOps = renew(transactions, distributor, idx)
  # todo: sub-functions (and outputs?) for claririty
  for balanceIDs, data in getClaimableBalancesData(queryAsset).items():
    transactions[idx].append_clawback_op(balance_id = data["id"])
    newNumRestrictedShares = data["amount"] * ratio
    rounded = roundUp(newNumRestrictedShares)
    recordDifference += rounded - newNumRestrictedShares
    transactions[idx].append_create_claimable_balance_op(
      asset = Asset(queryAsset, BT_ISSUER),
      amount = rounded,
      claimants = [
        Claimant(
          destination = data["recipient"],
          predicate = predicate_not(predicate_before_relative_time(data["release"]))
        )
      ]
    )
    numTxnOps += 2
    if(checkLimit(numTxnOps)):
      transactions[idx] = prep(transactions[idx], reason)
      transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
      idx, numTxnOps = renew(transactions, issuer, idx)
  transactions[idx] = prep(transactions[idx], reason)
  transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
  displayDifference(recordDifference)
  return transactions

