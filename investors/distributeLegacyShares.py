import sys
sys.path.append("../")
from globals import *

def distributeLegacyShares(account, queryAsset, amount, basis, vestingDate):
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, distributor)
  transactions[0].append_create_claimable_balance_op(
    asset = getAssetObjFromCode(queryAsset),
    amount = amount,
    claimants = [
      Claimant(
        destination = account,
        predicate = ClaimPredicate.predicate_unconditional() if not vestingDate else ClaimPredicate.predicate_not(
          ClaimPredicate.predicate_before_absolute_time(
            epochFromDay(
              pandas.to_datetime(vestingDate)
            )
          )
        )
      )
    ]
  )
  txn = transactions[0].set_timeout(90).add_text_memo(basis).build()
  txn.sign(Keypair.from_secret(DISTRIBUTOR_KEY))
  response = submitTxnGuaranteed(txn)
  claimableBalanceID = ""
  with open(f"{G_DIR}/docs/.well-known/distribution-bases.toml", "a") as cache:
    cache.write(f"{claimableBalanceID} = \"{basis}\"\n")

# Basis tracking, -> investor app, document with BIP paths
# distributeLegacyShares(BT_TREASURY, "DEMO", "10.4983211", "10|2009-9-9", "2023-1-1")
# distributeLegacyShares(BT_TREASURY, "DEMO", "10.4983211", "10|2009-9-9", "")