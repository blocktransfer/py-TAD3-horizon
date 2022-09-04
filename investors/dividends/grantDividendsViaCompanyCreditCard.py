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
  inFile = open(recordDateShareholdersOptedForCashDividendsCSV)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split("\n")
  inFile.close()
  print("*****\nDistributing dividend of $" + str(perShareDividend) + " per share\n*****\n")
  divSum = 0
  investorSum = 0
  mergedCardDividendsMSF = open("Card dividends distributed on {datetime.now().date()}.csv", "a")
  mergedCardDividendsMSF.write("Dividends Paid,Registration,Email,Routing # Direct Deposit,Account # Direct Deposit,Card # Card Deposit,Card CVV Card Deposit,Expiration Date Card Deposit,Billing Zip Card Deposit,For Internal Use: Card ID,Address,Address Extra,City,State,Postal Code,Country\n")
  mergedCardDividendsMSF.close()
  for lines in readFile[1:]:
    lines = lines.split(",")
    if lines[4] != "": continue
    shareholderDividend = float(lines[0]) * perShareDividend
    r = requests.get(USBankCaaSAPI + "vcards/" + lines[9] + "/details",  headers = {"Accept": "application/json", "Authorization": USBankAuthorization})
    if r.status_code == 400 or r.status_code == 404:
      transferCredit = 0
    else:
      currentCardLimit = r.json()["vcard"]["balances"]["availableCredit"]
      currentCardBalance = r.json()["vcard"]["balances"]["currentBalance"]
      transferCredit = currentCardLimit - currentCardBalance
      r = requests.post(USBankCaaSAPI + "vcards/" + lines[9] + "/close", headers = {"Accept": "application/json", "Authorization": USBankAuthorization})
      print("{}. Transferring remaining ${:.2f}:".format(r.json()["status"]["details"][0]["attributeName"], transferCredit))
    cardholderName = HumanName(lines[1])
    USBankAPIbody = {
    "amount": float("{:.2f}".format(transferCredit + shareholderDividend if shareholderDividend + transferCredit <= 50000 else 50000)),
    "cardInfo": {
      "firstName": cardholderName.first,
      "lastName": cardholderName.last,
      "email": lines[2]
    },
    "effectiveUntil": str(datetime.now().date() + timedelta(days = 365)),
    "paymentAccountID": USBankAccountID,
    "comments": [
      {
        "comment": lines[1],
        "comment": "{}, {}{}, {} {}, {}".format(lines[7], lines[8] + ", " if lines[8] !="" else "", lines[12], lines[13], lines[14], lines[15])
      }
    ],
    "returnCVV": True
    }
    r = requests.post(USBankCaaSAPI + "vcard",  headers = USBankAPIheaders, data = json.dumps(USBankAPIbody, indent=4))
    cardNum = r.json()["virtualCard"]["number"]
    cardCVV = r.json()["virtualCard"]["CVV"]
    cardExp = r.json()["virtualCard"]["expirationDate"]
    cardZip = r.json()["virtualCard"]["zip"]
    cardID = r.json()["virtualCard"]["ID"]
    mergedCardDividendsMSF = open("Card dividends distributed on {}.csv".format(datetime.now().date()), "a")
    mergedCardDividendsMSF.write("{:.2f},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(shareholderDividend, lines[1], lines[2], lines[3], lines[4], cardNum, cardCVV, cardExp, cardZip, cardID, lines[10], lines[11], lines[12], lines[13], lines[14], lines[15]))
    mergedCardDividendsMSF.close()
    print("Card ID {} created for {} with {:.2f} from dividends of ${} per share\nTotal card limit: ${:.2f}\n***\n".format(cardID, lines[1], shareholderDividend, perShareDividend, transferCredit + shareholderDividend))
    divSum += shareholderDividend
    investorSum += 1
  print("\n*****\n\nTotal of ${:.2f} cash dividends direct deposited to {} securityholders\n\n*****\n".format(divSum, investorSum))

grantDividendsViaCompanyCreditCard("demoCashDividendsMSF.csv", .23)
