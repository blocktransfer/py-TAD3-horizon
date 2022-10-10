import sys
sys.path.append("../")
from globals import *

def getMergedReportForAssetWithNumRestrictedSharesUsingMSF(queryAsset, numRestrictedShares, unclaimedMSF):
  StellarBlockchainBalances = getStellarBlockchainBalances(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares)
  mergeBlockchainRecordsWithMSF(queryAsset, unclaimedMSF, totalOutstandingShares, StellarBlockchainBalances)
  generateInternalRecord(queryAsset, StellarBlockchainBalances)

def getTotalOutstandingShares(queryAsset, numRestrictedShares):
  requestAddr = f"{HORIZON_INST}/assets?asset_code={queryAsset}&asset_issuer={BT_ISSUER}"
  data = requests.get(requestAddr).json()
  try:
    numUnrestrictedShares = Decimal(data["_embedded"]["records"][0]["amount"])
  except Exception:
    sys.exit("Input parameter error")
  totalOutstandingShares = Decimal(numRestrictedShares) + numUnrestrictedShares
  return totalOutstandingShares

def mergeBlockchainRecordsWithMSF(queryAsset, unclaimedMSFinst, totalOutstandingShares, StellarBlockchainBalances):
  MICR = open(MICR_TXT)
  next(MICR)
  unclaimedMSF = open(unclaimedMSFinst)
  next(unclaimedMSF)
  day = datetime.now().strftime("%Y-%m-%d at %H%M")
  mergedMSF = open(f"{G_DIR}/../pii/outputs/{queryAsset} MSF as of {day}.txt", "w")
  mergedMSF.write("Registration|Address|Email|Shares\n")
  for accounts in unclaimedMSF:
    account = accounts.split("|")
    cancelled = account[10]
    if(not cancelled):
      address = toFullAddress(
        account[3],
        account[4],
        account[5],
        account[6],
        account[7],
        account[8]
      )
      output = [
        account[1],
        address,
        "",
        account[0],
        account[11]
      ] # assume no email from old TA
      mergedMSF.write("|".join(output) + "\n")
  unclaimedMSF.close()
  for accounts in MICR:
    account = accounts.split("|")
    try:
      blockchainBalance = StellarBlockchainBalances[account[0]]
      if(not blockchainBalance):
        continue
    except KeyError:
      continue
    address = toFullAddress(
      account[4],
      account[5],
      account[6],
      account[7],
      account[8],
      account[9]
    )
    output = [
      account[1],
      address,
      account[2],
      str(blockchainBalance)
    ]
    mergedMSF.write("|".join(output) + "\n")
  MICR.close()
  mergedMSF.close()

def generateInternalRecord(queryAsset, StellarBlockchainBalances):
  internalRecord = open(f"{G_DIR}/../pii/outputs/{queryAsset}.txt", "w")
  internalRecord.write(f"Public Key|Balance||Blockchain snapshot at {datetime.now()}\n")
  for addresses, balances in StellarBlockchainBalances.items():
    internalRecord.write(f"'|'.join([addresses, str(balances)])\n")
  internalRecord.close()

