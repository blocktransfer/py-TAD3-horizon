import sys
sys.path.append("../../")
from globals import *

postSplitFileName = "[FORWARD] {} Post-Split Master Securityholder File.csv"

# testing: forwardSplit("StellarMart", 5, 2, "preSplitVeryRealStockIncMSF.csv")
def forwardSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesCSV):
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator > denominator 
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  outputPostSplitMSFwithUnclaimedShareholdersOnly = grantMSFnewSplitSharesUnclaimedOnStellarInclRestricted(MSFpreSplitBalancesCSV, numerator, denominator, queryAsset)
  newShareTxnXDRarr = []
  newShareTxnXDRarr = grantNewSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator)
  exportSplitNewShareTransactions(newShareTxnXDRarr)
  generateFinalPostSplitMSF(outputPostSplitMSFwithUnclaimedShareholdersOnly, MSFpreSplitBalancesCSV, queryAsset)

def grantMSFnewSplitSharesUnclaimedOnStellarInclRestricted(MSFpreSplitBalancesCSV, numerator, denominator, queryAsset):
  MSF = open(MSFpreSplitBalancesCSV, "r")
  oldMSF = MSF.read()
  oldMSF = oldMSF.strip()
  oldMSF = oldMSF.split("\n")
  MSF.close()
  newMSF = open(postSplitFileName.format(queryAsset), "w")
  newMSF.write(oldMSF[0] + "\n")
  for shareholder in oldMSF[1:]: # Assume restricted entries are separate from unrestricted entries 
    shareholder = shareholder.split(",")
    if(shareholder[0] == ""):
      sharesAfterSplit = Decimal(shareholder[1]) * numerator / denominator
      shareholder[1] = str(sharesAfterSplit)
      newMSF.write(",".join(shareholder) + "\n")
  newMSF.close()
  return newMSF

def grantNewSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator):
  server = Server(horizon_url= "https://" + HORIZON_INST)
  distributor = server.load_account(account_id = BT_DISTRIBUTOR)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_FEE
  transactions = []
  transactions.append(
    TransactionBuilder(
      source_account = distributor,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )
  reason = str(numerator) + "-for-" + str(denominator) + " forward stock split"
  i = idx = 0
  #pprint(StellarBlockchainBalances['GDWFWKFOXYGT6EHB2WYUPVKZFV7WDSOJQWMLDRIBQGDAUI3ADQOB5JKZ'])
  for addresses, balances in StellarBlockchainBalances.items():
    sharesToPay = (balances * numerator / denominator) - balances
    if(sharesToPay):
      transactions[idx].append_payment_op(
        destination = addresses,
        asset = Asset(queryAsset, BT_ISSUER),
        amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesToPay), )
      i += 1
    if(i >= MAX_NUM_TXN_OPS):
      transactions[idx].add_text_memo(reason).set_timeout(7200).build()
      i = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = distributor,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx].add_text_memo(reason).set_timeout(7200).build()
  return transactions

def exportSplitNewShareTransactions(txnXDRarr):
  for bulkTxnXDR in txnXDRarr:
    output = open(str(datetime.now()) + " forwardSplitPaymentXDR.txt", "w")
    output.write(str(bulkTxnXDR))
    output.close()

def generateFinalPostSplitMSF(outputMSF, MSFpreSplitBalancesCSV, queryAsset):
  finalMSF = open(postSplitFileName.format(queryAsset), "a")
  oldMSF = open(MSFpreSplitBalancesCSV, "r")
  readData = oldMSF.read()
  readData = readData.strip()
  readData = readData.split("\n")
  oldMSF.close()
  for shareholder in readData[1:]:
    shareholder = shareholder.split(",")
    if(shareholder[0]):
      finalMSF.write(",".join(shareholder) + "\n")
  finalMSF.close()

forwardSplit("StellarMart", 5, 2, "preSplitVeryRealStockIncMSF.csv")