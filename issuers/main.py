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
  addressPhysicalLine1 = lines[6]
  addressPhysicalLine2 = lines[7]
  addressCity = lines[8]
  addressStateProvince = lines[9]
  addressAreaCode = lines[10]
  SSN = lines[11]
  EIN = lines[12]
  TIN = lines[13]
  driversLicenseNumber = lines[14]
  passportNumber = lines[15]
  otherID = lines[16]
  onboardedDate = lines[17]
  otherKYCinternal = lines[18]
  email = lines[19]
  for account,balance in accountBalancesStellar:
    if account == addressStellar:
      break
  balanceAsPercentOfOutstandingShares = 100 * float(balance) / totalOutstanding
  linkedAccounts.append((account, balance, balanceAsPercentOfOutstandingShares, nameInstitution, nameFirst, nameMiddle, nameLast, nameSuffix, addressPhysicalLine1, addressPhysicalLine2, addressCity, addressStateProvince, addressAreaCode, SSN, EIN, TIN, driversLicenseNumber, passportNumber, otherID, onboardedDate, otherKYCinternal, email))
  