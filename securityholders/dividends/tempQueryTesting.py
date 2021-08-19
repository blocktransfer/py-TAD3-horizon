import requests
import json
from datetime import datetime
from datetime import timedelta
from pprint import pprint

USBankCaaSAPI = 'https://alpha-api.usbank.com/innovation/bank-node/caas/v1/'
USBankAPIkey = '6HKCcpr2jijlT0H1QfluoNZ6NutndJNA'
USBankSecret = 'pS5I39aTLkuPDsJk'
USBankAuthorization = 'Basic NkhLQ2NwcjJqaWpsVDBIMVFmbHVvTlo2TnV0bmRKTkE6cFM1STM5YVRMa3VQRHNKaw=='
USBankCustomerID = '6053588662'
USBankAccountID = '947714798707'

USBankAPIheaders = {
    'Accept': 'application/json',
    'Authorization': USBankAuthorization,
    'Content-Type': 'application/json'
}




r = requests.get(USBankCaaSAPI + 'company/' + USBankCustomerID,  headers = {'Accept': 'application/json', 'Authorization': USBankAuthorization})
print('\nCards:')
pprint(r.json()['cards'])
print('')

r = requests.get(USBankCaaSAPI + 'account/' + USBankAccountID + '/cards/ACTIVE',  headers = {'Accept': 'application/json', 'Authorization': USBankAuthorization})
pprint(r.json())
print('')

r = requests.get(USBankCaaSAPI + 'company/' + USBankCustomerID + '/account',  headers = {'Accept': 'application/json', 'Authorization': USBankAuthorization})
print('LOC:')
pprint(r.json()['accounts'][0]['balances'])
print('')