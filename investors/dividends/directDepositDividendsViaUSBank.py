# Import MSF -> Record Date via StellarNonNative in blocktransfer/record-date repo

import sys
sys.path.append("../../")
from globals import *

USbankMoneyMovementSimAPI = "https://alpha-api.USbank.com/innovation/bank-node/money-movement/v1/"
USbankCoreBankingAPI = "https://alpha-api.USbank.com/innovation/bank-node/customer-accounts/v1/"
USbankAPIkey = "6HKCcpr2jijlT0H1QfluoNZ6NutndJNA"
USbankSecret = "pS5I39aTLkuPDsJk"
USbankAuthorization = "Basic NkhLQ2NwcjJqaWpsVDBIMVFmbHVvTlo2TnV0bmRKTkE6cFM1STM5YVRMa3VQRHNKaw=="
USbankCustomerID = "6700658872"
dividendsPayableAccountNumber = "936606647590"
USbankAccountID = "947714798707"

def directDepositDividendsViaUSbank(recordDateShareholdersOptedForCashDividendsCSV, perShareDividend):
  USbankAPIheaders = {
    "Accept": "application/json",
    "Authorization": USbankAuthorization,
    "Content-Type": "application/json"
  }
  divSum = investorSum = 0
  with open(recordDateShareholdersOptedForCashDividendsCSV) as cashDividendInvestors:
    next(cashDividendInvestors)
    print(f"*****\n\nDistributing dividend of ${str(perShareDividend)} per share\n\n*****\n")
    with open(f"Direct deposit dividends distributed on {datetime.now().date()}.csv", "a") as mergedDirectDividendsMSF:
      mergedDirectDividendsMSF.write(
        "Dividends Paid,Registration,Email,Routing # Direct Deposit,Account # Direct Deposit,Card # Card Deposit,Card CVV Card Deposit,Expiration Date Card Deposit,Billing Zip Card Deposit,For Internal Use: Card ID,Address,Address Extra,City,State,Postal Code,Country\n"
      )
    for lines in cashDividendInvestors:
      lines = lines.split("|")
      if lines[5] != "":
          continue
      shareholderDividend = float(lines[0]) * perShareDividend
      USbankAPIbody = {
          "accountID": dividendsPayableAccountNumber,
          "amount": float(f"{shareholderDividend if shareholderDividend <= 10000 else 10000:.2f}"),
          "party": lines[1].replace("&", "and").replace("|", "").replace(".", "").replace("-", " ")
      }
      if USbankAPIbody["amount"] <= 0.00: continue
      r = requests.post(USbankMoneyMovementSimAPI + "activity/withdrawal", headers=USbankAPIheaders, data=json.dumps(USbankAPIbody))
      try:
        transactionID = r.json()["transactionID"]
      except Exception: continue
      with open(f"Direct deposit dividends distributed on {datetime.now().date()}.csv", "a") as mergedDirectDividendsMSF:
        mergedDirectDividendsMSF.write("|"
          .join(
            [
              f"{shareholderDividend:.2f}",
              lines[1],
              lines[2],
              lines[3],
              lines[4],
              "",
              "",
              "",
              "",
              "",
              lines[10],
              lines[11],
              lines[12],
              lines[13],
              lines[14],
              lines[15]
            ]
          ) + "\n")
      print(f"*** {lines[1]} compensated ${shareholderDividend:.2f} via dividend withdrawal #{transactionID} ***\n")
      divSum += shareholderDividend
      investorSum += 1
      # break # testing: prevent MAX_CARDS
  print("\n*****\n\nTotal of ${divSum:.2f} cash dividends direct deposited to {investorSum} security holders\n\n*****\n")


directDepositDividendsViaUSbank("demoCashDividendsMSF.csv", .0023)
