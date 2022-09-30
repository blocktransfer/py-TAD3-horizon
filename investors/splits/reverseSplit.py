from splitHelper import *

# testing: reverseSplit("StellarMart", 1, 10, "preSplitVeryRealStockIncMSF.txt")
def reverseSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesTXT):
  postSplitFileName = f"[REVERSE] {queryAsset} Post-Split Master Securityholder File.txt"
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator < denominator 
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  newShareTxnArr = revokeOldSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator)
  exportSplitNewShareTransactions(newShareTxnArr, queryAsset)
  generatePostSplitMSF(MSFpreSplitBalancesTXT, numerator, denominator, postSplitFileName)

def revokeOldSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator):
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  reason = f"NOTICE: {numerator}-for-{denominator} reverse split"
  numTxnOps = idx = 0
  for addresses, balances in StellarBlockchainBalances.items():
    sharesToClawback = balances - (balances * numerator / denominator)
    if(sharesToClawback):
      numTxnOps += 1
      transactions[idx].append_clawback_op(
        asset = Asset(queryAsset, BT_ISSUER),
        from_ = addresses,
        amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesToClawback),
      )
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(7200).build()
      transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
      numTxnOps = 0
      idx += 1
      appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(7200).build()
  transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
  return transactions

