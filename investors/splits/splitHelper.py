import sys
sys.path.append("../../")
from globals import *

def prep(transaction, reason):
  return transaction.add_text_memo(reason).set_timeout(7200).build()

def checkLimit(numTxnOps):
  return numTxnOps >= MAX_NUM_TXN_OPS

def renew(transactions, source, idx):
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, source)
  idx += 1
  return idx, 0

def generatePostSplitMSF(MSFpreSplitBalancesTXT, numerator, denominator, postSplitFileName):
  oldMSF = open(MSFpreSplitBalancesTXT)
  newMSF = open(postSplitFileName, "w")
  newMSF.write(next(oldMSF) + "\n")
  for accounts in oldMSF:
    account = accounts.split("|")
    if(account[1]):
      sharesAfterSplit = Decimal(account[1]) * numerator / denominator
      account[1] = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesAfterSplit) # todo: test rounding errors
      newMSF.write(f"{'|'.join(account)}")
    else:
      newMSF.write(f"{'|'.join(account)}")
  oldMSF.close()
  newMSF.close()
  return newMSF

def exportSplitNewShareTransactions(txnArr, queryAsset):
  for txns in txnArr:
    output = open(f"{str(datetime.now()).replace(':','.')} {queryAsset} StockSplitOutputXDR.txt", "w")
    output.write(txns.to_xdr())
    output.close()

def getClaimableBalancesData(queryAsset):
  claimableBalanceIDsMappedToData = data = {}
  requestAddr = f"{HORIZON_INST}/claimable_balances?asset={queryAsset}:{BT_ISSUER}&{MAX_SEARCH}"
  ledger = requests.get(requestAddr).json()
  while(ledger["_embedded"]["records"]):
    for claimableBalances in ledger["_embedded"]["records"]:
      if(len(claimableBalances["claimants"]) > 1):
        print(f"Malformed\n{claimableBalances}")
        continue
        #sys.exit("Critical operational error")
      data["amount"] = Decimal(claimableBalances["amount"]),
      data["recipient"] = claimableBalances["claimaints"][0]["destination"],
      data["release"] = claimableBalances["claimaints"][0]["not"]["abs_before_epoch"]
      claimableBalanceIDsMappedToData[claimableBalances["id"]] = data
    ledger = getNextLedgerData(ledger)
  return claimableBalanceIDsMappedToData

