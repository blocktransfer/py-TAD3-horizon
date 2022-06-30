from splitHelper import *

try:
  SECRET = sys.argv[1]
except:
  print("Running without key")

# testing: forwardSplit("StellarMart", 5, 2, "preSplitVeryRealStockIncMSF.csv")
def forwardSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesCSV):
  postSplitFileName = "[FORWARD] {} Post-Split Master Securityholder File.csv".format(queryAsset)
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator > denominator 
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  newShareTxnArr = grantNewSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator)
  exportSplitNewShareTransactions(newShareTxnArr, queryAsset)
  generatePostSplitMSF(MSFpreSplitBalancesCSV, numerator, denominator, postSplitFileName)

def grantNewSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator):
  transactions = []
  transactions.append(
    TransactionBuilder(
      source_account = distributor,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )
  reason = "NOTICE: {}-for-{} forward split".format(numerator, denominator)
  numTxnOps = idx = 0
  for addresses, balances in StellarBlockchainBalances.items():
    sharesToPay = (balances * numerator / denominator) - balances
    if(sharesToPay):
      numTxnOps += 1
      transactions[idx].append_payment_op(
        destination = addresses,
        asset = Asset(queryAsset, BT_ISSUER),
        amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesToPay),
      )
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(7200).build()
      transactions[idx].sign(Keypair.from_secret(SECRET))
      numTxnOps = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = distributor,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(7200).build()
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

