import sys
sys.path.append("../")
from globals import *

def getMergedReportForAssetWithNumRestrictedSharesUsingMSF(queryAsset, numRestrictedShares, unclaimedMSF):
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares)
  mergeBlockchainRecordsWithMSF(queryAsset, unclaimedMSF, totalOutstandingShares, StellarBlockchainBalances)
  generateInternalRecord(queryAsset, StellarBlockchainBalances)

def getTotalOutstandingShares(queryAsset, numRestrictedShares):
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_code=" + queryAsset + "&asset_issuer=" + BT_ISSUER
  data = requests.get(requestAddress).json()
  try:
    numUnrestrictedShares = Decimal(data["_embedded"]["records"][0]["amount"])
  except Exception:
    sys.exit("Input parameter error")
  totalOutstandingShares = Decimal(numRestrictedShares) + numUnrestrictedShares
  return totalOutstandingShares

def mergeBlockchainRecordsWithMSF(queryAsset, unclaimedMSFinst, totalOutstandingShares, StellarBlockchainBalances):
  inFile = open(unclaimedMSFinst)
  unclaimedMSF = inFile.read().strip().split("\n")
  inFile.close()
  inFile = open(MICR_CSV)
  MICR = inFile.read().strip().split("\n")
  inFile.close()
  mergedMSF = open("{} Master Securityholder File as of {}.csv".format(queryAsset, datetime.now().strftime("%Y-%m-%d at %H%M")), "w")
  mergedMSF.write("Registration,Address,Email,Shares\n")
  for lines in unclaimedMSF[1:]:
    lines = lines.split(",")
    cancelled = lines[10]
    if(not cancelled):
      address = toFullAddress(lines[3], lines[4], lines[5], lines[6], lines[7], lines[8])
      output = [lines[1], address, "", lines[0], lines[11]] # assume no email from old TA
      mergedMSF.write(",".join(output) + "\n")
  for lines in MICR[1:]:
    lines = lines.split(",")
    try:
      blockchainBalance = StellarBlockchainBalances[lines[0]]
      if(not blockchainBalance):
        continue
    except KeyError:
      continue
    address = toFullAddress(lines[4], lines[5], lines[6], lines[7], lines[8], lines[9])
    output = [lines[1], address, lines[2], str(blockchainBalance)]
    mergedMSF.write(",".join(output) + "\n")
  mergedMSF.close()

def generateInternalRecord(queryAsset, StellarBlockchainBalances):
  internalRecord = open("{}.csv".format(queryAsset), "w")
  internalRecord.write("Public Key,Balance,,Blockchain snapshot: {}\n".format(datetime.now()))
  for addresses, balances in StellarBlockchainBalances.items():
    internalRecord.write(",".join([addresses, str(balances)]) + "\n")
  internalRecord.close()

getMergedReportForAssetWithNumRestrictedSharesUsingMSF("DEMO", "0", "VeryRealStockIncUnclaimedMSF.csv")