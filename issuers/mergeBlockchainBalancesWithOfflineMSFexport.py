import sys
sys.path.append("../")
from globals import *

def getMergedReportForAssetWithNumRestrictedSharesUsingMSF(queryAsset, numRestrictedShares, unclaimedMSF):
  ledgerBalances = getLedgerBalances(queryAsset)
  totalOutstandingShares = getNumOutstandingShares(queryAsset, numRestrictedShares)
  mergeBlockchainRecordsWithMSF(queryAsset, unclaimedMSF, totalOutstandingShares, ledgerBalances)
  generateInternalRecord(queryAsset, ledgerBalances)

def mergeBlockchainRecordsWithMSF(queryAsset, unclaimedMSFinst, totalOutstandingShares, ledgerBalances):
  day = datetime.now().strftime("%Y-%m-%d at %H%M")
  with open(MICR_TXT) as MICR:
    with open(unclaimedMSFinst) as unclaimedMSF:
      with open(f"{MICR_DIR}/outputs/{queryAsset} MSF as of {day}.txt", "w") as mergedMSF:
        next(MICR)
        next(unclaimedMSF)
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
        for accounts in MICR:
          account = accounts.split("|")
          try:
            blockchainBalance = ledgerBalances[account[0]]
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

def generateInternalRecord(queryAsset, ledgerBalances):
  with (f"{MICR_DIR}/outputs/{queryAsset}.txt", "w") as internalRecord:
    internalRecord.write(f"Public Key|Balance||Blockchain snapshot at {datetime.now()}\n")
    for addresses, balances in ledgerBalances.items():
      internalRecord.write(f"'|'.join([addresses, str(balances)])\n")

