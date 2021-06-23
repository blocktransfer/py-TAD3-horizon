import requests
from pprint import pprint

queryAsset = 'StellarMart'
restrictedShares = 69420
limit = '200'
horizonInstance = 'horizon.stellar.org'
BTIssuer = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM'
requestAddress = 'https://' + horizonInstance + '/accounts?asset=' + queryAsset + ':' + BTIssuer + '&limit=' + limit

accountBalancesStellar = []
while(True):
  r = requests.get(requestAddress)
  data = r.json()
  embeddedRecords=data['_embedded']['records']
  if embeddedRecords == []:
    break
  for account in embeddedRecords:
    accountAddress = account['id']
    for balances in account['balances']:
      if balances['asset_type'] != 'native' and balances['asset_code'] == queryAsset:
        accountBalance = balances['balance']
    accountBalancesStellar.append((accountAddress, accountBalance))
  requestAddress = data['_links']['next']['href'].replace('%3A', ':')

requestAddress = 'https://' + horizonInstance + '/ledgers?asset=' + queryAsset + ':' + BTIssuer
r = requests.get(requestAddress)
data = r.json()
unrestrictedShares = data['_embedded']['records'][len(data['_embedded']['records']) - 1]['total_coins']
totalOutstanding = float(restrictedShares) + float(unrestrictedShares)

PIIcsvName = "insecureStockTestSheet.csv"
inFile = open(PIIcsvName)
readFile = inFile.read()
readFile = readFile.strip()
readFile = readFile.split('\n')
inFile.close()

linkedAccounts = []
for lines in readFile:
  lines = lines.split(',')
  addressStellar = lines[0]
  if addressStellar == 'Blockchain Address':
    continue
  nameInstitution = lines[1]
  nameFirst = lines[2]
  nameMiddle = lines[3]
  nameLast = lines[4]
  nameSuffix = lines[5]
  addressPhysical = lines[6]
  addressCity = lines[7]
  addressStateProvince = lines[8]
  addressAreaCode = lines[9]
  SSN = lines[10]
  EIN = lines[11]
  TIN = lines[12]
  driversLicenseNumber = lines[13]
  passportNumber = lines[14]
  otherID = lines[15]
  onboardedDate = lines[16]
  otherKYCinternal = lines[17]
  email = lines[18]
  for account,balance in accountBalancesStellar:
    if account == addressStellar:
      break
  balanceAsPercentOfOutstandingShares = 100 * float(balance) / totalOutstanding
  linkedAccounts.append((account, balance, balanceAsPercentOfOutstandingShares, nameInstitution, nameFirst, nameMiddle, nameLast, nameSuffix, addressPhysical, addressCity, addressStateProvince, addressAreaCode, SSN, EIN, TIN, driversLicenseNumber, passportNumber, otherID, onboardedDate, otherKYCinternal, email))