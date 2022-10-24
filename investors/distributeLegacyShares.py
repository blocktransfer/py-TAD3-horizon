import sys
sys.path.append("../")
from globals import *

def distributeLegacyShares(account, queryAsset, amount, basis, vestingDate):
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, distributor)
  transactions[0].append_create_claimable_balance_op(
    asset = Asset(queryAsset, BT_ISSUER),
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
  a = transactions[0].set_timeout(30).add_text_memo("").build()
  a.sign(Keypair.from_secret(DISTRIBUTOR_KEY))
  print(a.to_xdr())
  #getAllInvestors # global func 
  #availableLumensDict = getAddrsMappedToAvailableLumens(allInvestors)
  #replenishTxn = replenishDepletedBalances(availableLumensDict) # impliment some kind of way to watch for misuse
  #exportTxn # global

def onboardNewAccounts():
  # read MICR -> accounts cache 
  return 1

distributeLegacyShares(BT_TREASURY, "DEMO", "10.4983211", "10|2009-9-9", "2023-1-1")
distributeLegacyShares(BT_TREASURY, "DEMO", "10.4983211", "10|2009-9-9", "")