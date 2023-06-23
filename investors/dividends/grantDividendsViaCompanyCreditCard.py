import requests
import json
from datetime import datetime
from datetime import timedelta
from nameparser import HumanName

USBankCaaSAPI = "https://alpha-api.usbank.com/innovation/bank-node/caas/v1/"
USBankAPIkey = "6HKCcpr2jijlT0H1QfluoNZ6NutndJNA"
USBankSecret = "pS5I39aTLkuPDsJk"
USBankAuthorization = "Basic NkhLQ2NwcjJqaWpsVDBIMVFmbHVvTlo2TnV0bmRKTkE6cFM1STM5YVRMa3VQRHNKaw=="
USBankCompanyID = "6053588662"
USBankAccountID = "947714798707"

def grantDividendsViaCompanyCreditCard(recordDateShareholdersOptedForCashDividendsCSV, perShareDividend):
  USBankAPIheaders = {
    "Accept": "application/json",
    "Authorization": USBankAuthorization,
    "Content-Type": "application/json"
  }
  totalDividends = investorSum = 0

  with open(recordDateShareholdersOptedForCashDividendsCSV) as inFile:
    next(inFile)
    readFile = [line.strip().split(",") for line in inFile]

    print(f"*****\nDistributing dividend of ${perShareDividend} per share\n*****\n")

    with open(f"Card dividends distributed on {datetime.now().date()}.csv", "a") as mergedCardDividendsMSF:
      mergedCardDividendsMSF.write("Dividends Paid,Registration,Email,Routing # Direct Deposit,Account # Direct Deposit,Card # Card Deposit,Card CVV Card Deposit,Expiration Date Card Deposit,Billing Zip Card Deposit,For Internal Use: Card ID,Address,Address Extra,City,State,Postal Code,Country\n")

      for lines in readFile[1:]:
        if lines[4] != "":
          continue

        shareholderDividend = float(lines[0]) * perShareDividend

        r = requests.get(USBankCaaSAPI + f"vcards/{lines[9]}/details", headers={"Accept": "application/json", "Authorization": USBankAuthorization})

        if r.status_code == 400 or r.status_code == 404:
          transferCredit = 0
        else:
          currentCardLimit = r.json()["vcard"]["balances"]["availableCredit"]
          currentCardBalance = r.json()["vcard"]["balances"]["currentBalance"]
          transferCredit = currentCardLimit - currentCardBalance
          r = requests.post(USBankCaaSAPI + f"vcards/{lines[9]}/close", headers={"Accept": "application/json", "Authorization": USBankAuthorization})
          print(f"{r.json()['status']['details'][0]['attributeName']}. Transferring remaining ${transferCredit:.2f}:")

        cardholderName = HumanName(lines[1])
        USBankAPIbody = {
          "amount": float(f"{transferCredit + shareholderDividend:.2f}" if shareholderDividend + transferCredit <= 50000 else "50000"),
          "cardInfo": {
            "firstName": cardholderName.first,
            "lastName": cardholderName.last,
            "email": lines[2]
          },
          "effectiveUntil": str(datetime.now().date() + timedelta(days=365)),
          "paymentAccountID": USBankAccountID,
          "comments": [
            {
              "comment": lines[1],
              "comment": f"{lines[7]}, {lines[8] + ', ' if lines[8] != '' else ''}{lines[12]}, {lines[13]}, {lines[14]}, {lines[15]}"
            }
          ],
          "returnCVV": True
        }

        r = requests.post(USBankCaaSAPI + "vcard", headers=USBankAPIheaders, data=json.dumps(USBankAPIbody, indent=4))

        cardNum = r.json()["virtualCard"]["number"]
        cardCVV = r.json()["virtualCard"]["CVV"]
        cardExp = r.json()["virtualCard"]["expirationDate"]
        cardZip = r.json()["virtualCard"]["zip"]
        cardID = r.json()["virtualCard"]["ID"]

        mergedCardDividendsMSF.write(f"{shareholderDividend:.2f},{lines[1]},{lines[2]},{lines[3]},{lines[4]},{cardNum},{cardCVV},{cardExp},{cardZip},{cardID},{lines[10]},{lines[11]},{lines[12]},{lines[13]},{lines[14]},{lines[15]}\n")

        print(f"Card ID {cardID} created for {lines[1]} with {shareholderDividend:.2f} from dividends of ${perShareDividend} per share")
        print(f"Total card limit: ${transferCredit + shareholderDividend:.2f}\n***\n")

        totalDividends += shareholderDividend
        investorSum += 1

    print(f"\n*****\n\nTotal of ${totalDividends:.2f} cash granted by virtual credit cards to {investorSum} securityholders\n\n*****\n")


grantDividendsViaCompanyCreditCard("demoCashDividendsMSF.csv", .23)
