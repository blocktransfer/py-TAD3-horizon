from datetime import datetime
from decimal import Decimal
import requests
import json

MAX_SEARCH = "200"
HORIZON_INST = "horizon.stellar.org"
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"

# testing: getMergedReportForAssetWithNumRestrictedSharesUsingMSF("StellarMart", 10000, "VeryRealStockIncMSF.csv")
# with BT_ISSUER = "GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM")
def getMergedReportForAssetWithNumRestrictedSharesUsingMSF(queryAsset, numRestrictedShares, MSF):
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares)
  didSucceed = mergeBlockchainRecordsWithMSF(queryAsset, MSF, totalOutstandingShares, StellarBlockchainBalances)
  return didSucceed

def getStellarBlockchainBalances(queryAsset):
  StellarBlockchainBalances = {}
  requestAddress = "https://" + HORIZON_INST + "/accounts?asset=" + queryAsset + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
  data = requests.get(requestAddress).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for accounts in blockchainRecords:
      accountAddress = accounts["id"]
      for balances in accounts["balances"]:
        if balances["asset_type"] != "native" and balances["asset_code"] == queryAsset:
          accountBalance = Decimal(balances["balance"])
          break
      StellarBlockchainBalances[accountAddress] = accountBalance
    # Go to next cursor
    requestAddress = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddress).json()
    blockchainRecords = data["_embedded"]["records"]
  return StellarBlockchainBalances

def getTotalOutstandingShares(queryAsset, numRestrictedShares):
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddress).json()
  numUnrestrictedShares = Decimal(data["_embedded"]["records"][0]["amount"])
  totalOutstandingShares = numRestrictedShares + numUnrestrictedShares
  return totalOutstandingShares

def mergeBlockchainRecordsWithMSF(queryAsset, MSF, totalOutstandingShares, StellarBlockchainBalances):
  inFile = open(MSF)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split("\n")
  inFile.close()
  mergedMSF = open("{} Master Securityholder File as of {}.csv".format(queryAsset, datetime.now()), "w")
  mergedMSF.write("Shares,Percent of Outstanding Shares,Registration,Email,Date of Birth / Organization,Address,Address Extra,City,State,Postal Code,Country,Onboarded Date,Issue Date of Security,Cancellation Date of Security,Dividends,Restricted Shares Notes\n")
  for lines in readFile[1:]:
    lines = lines.split(",")
    sharesNotYetClaimedOnStellar = 0 if lines[1] == "" else Decimal(lines[1])
    try:
        blockchainBalance = 0 if lines[0] == "" else StellarBlockchainBalances[lines[0]]
    except KeyError:
        # This address is no longer a securityholder per removed trustline. Prune from merged MSF
        continue
    totalBalance = blockchainBalance + sharesNotYetClaimedOnStellar # Redundant given restricted entries are separate from unrestricted entries 
    lines[0] = str(totalBalance)
    lines[1] = str(totalBalance / totalOutstandingShares)
    mergedMSF.write(",".join(lines) + "\n")
  mergedMSF.close()
  return True
