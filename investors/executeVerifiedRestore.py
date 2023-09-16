import sys
sys.path.append("../")
from globals import *

# basis tracking ?

memo = "Verified Restore 🔏"

def executeVerifiedRestore(fromPK, toPK):
  server = Server("https://horizon.stellar.org")
  fromAcc = server.load_account(fromPK)
  transaction = TransactionBuilder(BT_ISSUERS[0])
  newClaimableBalances = []
  
  for claimableBalance in fromAcc.claimable_balances().records:
    claimableBalanceId = claimableBalance["id"]
    claimants = server.claimable_balance_claimants(claimableBalanceId).records

    newClaimableBalance = {
      "asset": claimableBalance["asset"],
      "amount": claimableBalance["amount"],
      "claimants": claimants,
      "sponsor": toPK,
    }
    newClaimableBalances.append(newClaimableBalance)

    transaction.append_operation(
      ClawbackOperation(
        asset = claimableBalance["asset"],
        from_ = toPK,
        amount = claimableBalance["amount"]
      )
    )

  for newClaimableBalance in newClaimableBalances:
    transaction.append_operation(
      PaymentOperation(
        destination = toPK,
        asset = newClaimableBalance["asset"],
        amount = newClaimableBalance["amount"]
      )
    )

    transaction.append_operation(
      ClaimableBalanceEntryOperation.create_claimable_balance_entry(
        asset = newClaimableBalance["asset"],
        amount = newClaimableBalance["amount"],
        claimants = newClaimableBalance["claimants"],
        claimant = toPK
      )
    )

  # add memo, timeout, ...
  transaction = transaction.build()
  transaction.sign(assetIssuerKeypair)
#globalized
#   try:
#     server.submit_transaction(transaction)
#   except Exception as e:
#     print(f"Error submitting transaction: {str(e)}")
