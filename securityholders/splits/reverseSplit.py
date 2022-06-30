from splitHelper import *

try:
  SECRET = sys.argv[1]
except:
  print("Running without key")

# testing: reverseSplit("StellarMart", 1, 10, "preSplitVeryRealStockIncMSF.csv")
def reverseSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesCSV):
  postSplitFileName = "[REVERSE] {} Post-Split Master Securityholder File.csv".format(queryAsset)
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator < denominator 
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  newShareTxnArr = revokeOldSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator)
  exportSplitNewShareTransactions(newShareTxnArr, queryAsset)
  generatePostSplitMSF(MSFpreSplitBalancesCSV, numerator, denominator, postSplitFileName)

def revokeOldSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator):
  transactions = []
  transactions.append(
    TransactionBuilder(
      source_account = issuer,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )
  reason = "NOTICE: {}-for-{} reverse split".format(numerator, denominator)
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
      transactions[idx].sign(Keypair.from_secret(SECRET))
      numTxnOps = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = issuer,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(7200).build()
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

