import requests

searchLimitMax200 = '200'
horizonInstance = 'horizon.stellar.org'
BTissuerAddress = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM'

# With "formattingStockTestSheet.csv", use "StellarMart" as queryAsset and any numRestrictedShares
def getMergedReportForAssetWithNumRestrictedSharesUsingPIIcsvFile(queryAsset, numRestrictedShares, PIIcsvSpreadsheetFileName):
  accountBalancesFromStellar = getAccountBalancesFromStellar(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares)
  mergedReport = mergeBlockchainRecordsWithPII(PIIcsvSpreadsheetFileName, totalOutstandingShares, accountBalancesFromStellar)
  return mergedReport

def getAccountBalancesFromStellar(queryAsset):
  accountBalancesFromStellar = []
  requestAddress = 'https://' + horizonInstance + '/accounts?asset=' + queryAsset + ':' + BTissuerAddress + '&limit=' + searchLimitMax200
  r = requests.get(requestAddress)
  data = r.json()
  blockchainRecords = data['_embedded']['records']
  while(blockchainRecords != []):
    for eachAccount in blockchainRecords:
      accountAddress = eachAccount['id']
      for balances in eachAccount['balances']:
        if balances['asset_type'] != 'native' and balances['asset_code'] == queryAsset:
          accountBalance = balances['balance']
          break
      accountBalancesFromStellar.append((accountAddress, accountBalance))
    # Go to next cursor
    requestAddress = data['_links']['next']['href'].replace('%3A', ':')
    r = requests.get(requestAddress)
    data = r.json()
    blockchainRecords = data['_embedded']['records']
  return accountBalancesFromStellar

def getTotalOutstandingShares(queryAsset, numRestrictedShares):
  requestAddress = 'https://' + horizonInstance + '/ledgers?asset=' + queryAsset + ':' + BTissuerAddress
  r = requests.get(requestAddress)
  data = r.json()
  numUnrestrictedShares = data['_embedded']['records'][len(data['_embedded']['records']) - 1]['total_coins']
  totalOutstandingShares = float(numRestrictedShares) + float(numUnrestrictedShares)
  return totalOutstandingShares

def mergeBlockchainRecordsWithPII(PIIcsvSpreadsheetFileName, totalOutstandingShares, accountBalancesStellar):
  inFile = open(PIIcsvSpreadsheetFileName)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split('\n')
  inFile.close()

  linkedAccounts = []
  for lines in readFile[1:]:
    lines = lines.split(',')
    addressStellar = lines[0]
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
    addressCountry = lines[11]
    SSN = lines[12]
    EIN = lines[13]
    TIN = lines[14]
    driversLicenseNumber = lines[15]
    passportNumber = lines[16]
    otherID = lines[17]
    onboardedDate = lines[18]
    otherKYCinternal = lines[19]
    email = lines[20]
    for account,balance in accountBalancesStellar:
      if account == addressStellar:
        break
    balanceAsPercentOfOutstandingShares = 100 * float(balance) / totalOutstandingShares
    linkedAccounts.append((account, balance, balanceAsPercentOfOutstandingShares, nameInstitution, nameFirst, nameMiddle, nameLast, nameSuffix, addressPhysicalLine1, addressPhysicalLine2, addressCity, addressStateProvince, addressAreaCode, addressCountry, SSN, EIN, TIN, driversLicenseNumber, passportNumber, otherID, onboardedDate, otherKYCinternal, email))
  return linkedAccounts
