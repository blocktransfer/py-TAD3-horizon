from stellar_sdk import Asset, Keypair, Server, TransactionBuilder
from datetime import datetime
from decimal import Decimal
import requests
import json

from root.parent.issuers.mergeBlockchainBalancesWithMSF import getStellarBlockchainBalances
sys.path.append(os.path.abspath("../issuers/"))
import mergeBlockchainBalancesWithMSF


HORIZON_INST = "horizon.stellar.org"
MAX_NUM_DECIMALS = "7"
FALLBACK_MIN_FEE = 100
MAX_NUM_TXN_OPS = 100
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
BT_DISTRIBUTOR = "GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6"

postSplitFileName = "{} Post-Split Master Securityholder File.csv"

def grantMSFnewSplitSharesUnclaimedOnStellarInclRestricted(MSFpreSplitBalancesCSV, numerator, denominator):
  MSF = open(MSFpreSplitBalancesCSV, "r")
  oldMSF = MSF.read()
  oldMSF = oldMSF.strip()
  oldMSF = oldMSF.split("\n")
  MSF.close()
  newMSF = open(postSplitFileName.format(queryAsset), "w")
  newMSF.write(oldMSF[0] + "\n")
  for shareholder in oldMSF[1:]: # Assume restricted entries are separate from unrestricted entries 
    if(shareholder[0] == ""):
      shareholder = shareholder.split(",")
      sharesAfterSplit = Decimal(shareholder[1]) * numerator / denominator
      shareholder[1] = str(sharesAfterSplit)
      newMSF.write(",".join(shareholder) + "\n")
  newMSF.close()
  return newMSF

def grantNewSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator):
  server = Server(horizon_url= "https://" + HORIZON_INST)
  distributor = server.load_account(account = BT_DISTRIBUTOR)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_FEE
  transactions[0] = TransactionBuilder(
    source_account = distributor,
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = fee, )
  reason = str(numerator) + "-for-" + str(denominator) + " forward stock split"
  i, idx = 0
  for address, balance in StellarBlockchainBalances:
    sharesToPay = (balance * numerator / denominator) - balance
    transactions[idx].append_payment_op(
      destination = address,
      asset = Asset(queryAsset, BT_ISSUER),
      amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(sharesToPay), )
    if(++i and i >= MAX_NUM_TXN_OPS):
      transactions[idx].add_text_memo(reason).set_timeout(7200).build()
      i = 0
      idx++
      transactions[idx] = TransactionBuilder(
        source_account = distributor,
        network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
        base_fee = fee, )
  transactions[idx].add_text_memo(reason).set_timeout(7200).build()
  return transactions

def exportSplitNewShareTransactions(txnXDRarr):
  for txn in txnXDRarr:
    output = open(datetime.now() + " forwardSplitPaymentXDR", "w")
    output.write(bulkTxnXDR)
    output.close()

def generateFinalPostSplitMSF(outputMSF, MSFpreSplitBalancesCSV):
  

def forwardSplit(queryAsset, numerator, denominator, MSFpreSplitBalancesCSV):
  numerator = Decimal(numerator)
  denominator = Decimal(denominator)
  assert numerator > denominator 
  StellarBlockchainBalances = mergeBlockchainBalancesWithMSF.getStellarBlockchainBalances(queryAsset)
  
  outputPostSplitMSFwithUnclaimedShareholdersOnly = grantMSFnewSplitSharesUnclaimedOnStellarInclRestricted(MSFpreSplitBalancesCSV, numerator, denominator)
  # ^ Outputs new postSplitMSF
  
  newShareTxnXDRarr = grantNewSplitSharesFromBalancesClaimedOnStellar(StellarBlockchainBalances, queryAsset, numerator, denominator)
  exportSplitNewShareTransactions(newShareTxnXDRarr)
  
  # ... now we use it
  generateFinalPostSplitMSF(outputPostSplitMSFwithUnclaimedShareholdersOnly, MSFpreSplitBalancesCSV)
  
  newMSF = open(postSplitFileName.format(queryAsset), "a")
  

