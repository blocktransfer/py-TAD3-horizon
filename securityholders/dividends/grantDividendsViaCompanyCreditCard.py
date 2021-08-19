# I, John Wooten of my own free will, hereby authorize U.S. Bank to freely use any materials
# disclosed herein for the distribution of secuirty dividends among its clients or affiliates.

import requests
import json
from datetime import datetime
from datetime import timedelta
from nameparser import HumanName

from pprint import pprint

USBankCaaSAPI = 'https://alpha-api.usbank.com/innovation/bank-node/caas/v1/'
USBankAPIkey = '6HKCcpr2jijlT0H1QfluoNZ6NutndJNA'
USBankSecret = 'pS5I39aTLkuPDsJk'
USBankAuthorization = 'Basic NkhLQ2NwcjJqaWpsVDBIMVFmbHVvTlo2TnV0bmRKTkE6cFM1STM5YVRMa3VQRHNKaw=='
USBankCompanyID = '6053588662'
USBankAccountID = '947714798707'

def grantDividendsViaCompanyCreditCard(recordDateShareholdersOptedForCashDividendsCSV, perShareDividend):
  USBankAPIheaders = {
    'Accept': 'application/json',
    'Authorization': USBankAuthorization,
    'Content-Type': 'application/json'
  }
  inFile = open(recordDateShareholdersOptedForCashDividendsCSV)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split('\n')
  inFile.close()
  print('*****\nDistributing dividend of $' + str(perShareDividend) + ' per share\n*****\n')
  divSum = 0
  investorSum = 0
  mergedCardDividendsMSF = open('Card dividends distributed on {}.csv'.format(datetime.now().date()), 'a')
  mergedCardDividendsMSF.write('Dividends Paid,Registration,Email,Routing # Direct Deposit,Account # Direct Deposit,Card # Card Deposit,Card CVV Card Deposit,Expiration Date Card Deposit,Billing Zip Card Deposit,For Internal Use: Card ID,Address,Address Extra,City,State,Postal Code,Country\n')
  mergedCardDividendsMSF.close()
  for lines in readFile[1:]:
    lines = lines.split(',')
    if lines[4] != '': continue
    shareholderDividend = float(lines[0]) * perShareDividend
    r = requests.get(USBankCaaSAPI + 'vcards/' + lines[9] + '/details',  headers = {'Accept': 'application/json', 'Authorization': USBankAuthorization})
    if r.status_code == 400 or r.status_code == 404:
      transferCredit = 0
    else:
      currentCardLimit = r.json()['vcard']['balances']['availableCredit']
      currentCardBalance = r.json()['vcard']['balances']['currentBalance']
      transferCredit = currentCardLimit - currentCardBalance
      r = requests.post(USBankCaaSAPI + 'vcards/' + lines[9] + '/close', headers = {'Accept': 'application/json', 'Authorization': USBankAuthorization})
    cardholderName = HumanName(lines[1])
    USBankAPIbody = {
    'amount': float('{:.2f}'.format(transferCredit + shareholderDividend if shareholderDividend + transferCredit <= 50000 else 50000)),
    'cardInfo': {
      'firstName': cardholderName.first,
      'lastName': cardholderName.last,
      'email': lines[2]
    },
    'effectiveUntil': str(datetime.now().date() + timedelta(days = 365)),
    'paymentAccountID': USBankAccountID,
    'comments': [
      {
        'comment': lines[1],
        'comment': '{}, {}{}, {} {}, {}'.format(lines[7], lines[8] + ', ' if lines[8] !='' else '', lines[9], lines[10], lines[11], lines[12])
      }
    ],
    'returnCVV': True
    }
    r = requests.post(USBankCaaSAPI + 'vcard',  headers = USBankAPIheaders, data = json.dumps(USBankAPIbody, indent=4))
    print(r.status_code, r.reason)
    pprint(r.json())
    print('')
    cardNum = r.json()['virtualCard']['number']
    cardCVV = r.json()['virtualCard']['CVV']
    cardExp = r.json()['virtualCard']['expirationDate']
    cardZip = r.json()['virtualCard']['zip']
    cardID = r.json()['virtualCard']['ID']
    mergedCardDividendsMSF = open('Card dividends distributed on {}.csv'.format(datetime.now().date()), 'a')
    mergedCardDividendsMSF.write('{:.2f},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(shareholderDividend, lines[1], lines[2], lines[3], lines[4], cardNum, cardCVV, cardExp, cardZip, cardID, lines[10], lines[11], lines[12], lines[13], lines[14], lines[15]))
    mergedCardDividendsMSF.close()
    print('${:.2f} added to credit limit on {}\'s card for dividend of ${} per share\nTotal card limit: ${:.2f}***\n'.format(shareholderDividend, lines[1], perShareDividend, transferCredit + shareholderDividend))
    divSum += shareholderDividend
    investorSum += 1
    break # testing: prevent MAX_CARDS
  print('\n*****\n\nTotal of ${:.2f} cash dividends direct deposited to {} securityholders\n\n*****\n'.format(divSum, investorSum))

grantDividendsViaCompanyCreditCard('demoCashDividendsMSF.csv', .23)
