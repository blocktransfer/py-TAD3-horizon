from splitHelper import *

# testing: reverseSplit("StellarMart", 1, 10, "preSplitVeryRealStockIncMSF.txt", "2022-1-18")
def reverseSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesTXT, recordDate):
  postSplitFileName = f"[REVERSE] {queryAsset} Post-Split Master Securityholder File.txt"
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator < denominator 
  ledgerBalances = getLedgerBalances(queryAsset)
  newShareTxnArr = revokeOldSplitSharesFromBalancesClaimedOnStellar(ledgerBalances, queryAsset, numerator, denominator, recordDate)
  exportSplitNewShareTransactions(newShareTxnArr, queryAsset)
  generatePostSplitMSF(MSFpreSplitBalancesTXT, numerator, denominator, postSplitFileName)

def revokeOldSplitSharesFromBalancesClaimedOnStellar(ledgerBalances, queryAsset, numerator, denominator, recordDate):
  transactions = []
  ratio = numerator / denominator
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  reason = f"{numerator}-for-{denominator} split ({recordDate})"
  numTxnOps = idx = 0
  for addresses, balances in ledgerBalances.items():
    sharesToClawback = balances - (balances * ratio)
    if(sharesToClawback):
      numTxnOps += 1
      transactions[idx].append_clawback_op(
        asset = Asset(queryAsset, BT_ISSUER),
        from_ = addresses,
        amount = sharesToClawback,
      )
    if(checkLimit(numTxnOps)):
      transactions[idx] = prep(transactions[idx], reason)
      transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
      idx, numTxnOps = renew(transactions, issuer, idx)
  for balanceIDs, data in getClaimableBalancesData(queryAsset).items():
    print(data["id"])
    newNumRestrictedShares = data["amount"] * ratio
    transactions[idx].append_clawback_op(balance_id = data["id"])
    transactions[idx].append_create_claimable_balance_op(
      asset = Asset(queryAsset, BT_ISSUER),
      amount = newNumRestrictedShares,
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
  return transactions

