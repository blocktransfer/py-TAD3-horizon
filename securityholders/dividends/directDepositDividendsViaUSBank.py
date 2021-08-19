# I, John Wooten of my own free will, hereby authorize U.S. Bank to freely use any materials
# disclosed herein for the distribution of secuirty dividends among its clients or affiliates.

# Import MSF -> Record Date via StellarNonNative in blocktransfer/record-date repo

import requests
import json
from datetime import datetime

from pprint import pprint 

USBankMoneyMovementSimAPI = 'https://alpha-api.usbank.com/innovation/bank-node/money-movement/v1/'
USBankCoreBankingAPI = 'https://alpha-api.usbank.com/innovation/bank-node/customer-accounts/v1/'
USBankAPIkey = '6HKCcpr2jijlT0H1QfluoNZ6NutndJNA'
USBankSecret = 'pS5I39aTLkuPDsJk'
USBankAuthorization = 'Basic NkhLQ2NwcjJqaWpsVDBIMVFmbHVvTlo2TnV0bmRKTkE6cFM1STM5YVRMa3VQRHNKaw=='
USBankCustomerID = '6700658872'
BlockTransferDividendsPayableAccountNum = '936606647590'
USBankAccountID = '947714798707'

def directDepositDividendsViaUSBank(recordDateShareholdersOptedForCashDividendsCSV, perShareDividend):
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
  mergedDirectDividendsMSF = open('Direct deposit dividends distributed on {}.csv'.format(datetime.now().date()), 'a')
  mergedDirectDividendsMSF.write('Dividends Paid,Registration,Email,Routing # Direct Deposit,Account # Direct Deposit,Card # Card Deposit,Card CVV Card Deposit,Expiration Date Card Deposit,Billing Zip Card Deposit,For Internal Use: Card ID,Address,Address Extra,City,State,Postal Code,Country\n')
  mergedDirectDividendsMSF.close()
  for lines in readFile[1:]:
    lines = lines.split(',')
    if lines[5] != '': continue
    shareholderDividend = float(lines[0]) * perShareDividend
    USBankAPIbody = {
      'customerID': USBankCustomerID,
      'accountID': BlockTransferDividendsPayableAccountNum,
      'routingNumber': lines[3],
      'externalAccountID': lines[4],
      'amount': float('{:.2f}'.format(shareholderDividend if shareholderDividend <= 10000 else 10000))
    }
    r = requests.post(USBankMoneyMovementSimAPI + 'activity/external-transfer',  headers = USBankAPIheaders, data = json.dumps(USBankAPIbody))
    print(r.status_code, r.reason)
    pprint(r.json())
    
    mergedDirectDividendsMSF = open('Direct deposit dividends distributed on {}.csv'.format(datetime.now().date()), 'a')
    mergedDirectDividendsMSF.write('{:.2f},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(shareholderDividend, lines[1], lines[2], lines[3], lines[4], '', '', '', '', '', lines[10], lines[11], lines[12], lines[13], lines[14], lines[15]))
    mergedDirectDividendsMSF.close()
    print( '*** {} compensated ${:.2f} for dividend of ${} per share via direct deposit ***\n'.format(lines[1], shareholderDividend, perShareDividend))
    divSum += shareholderDividend
    investorSum += 1
    break # testing: prevent MAX_CARDS
  print('\n*****\n\nTotal of ${:.2f} cash dividends direct deposited to {} securityholders\n\n*****\n'.format(divSum, investorSum))

directDepositDividendsViaUSBank('demoCashDividendsMSF.csv', .0000023)
