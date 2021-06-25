# A script to merge a given list of shareholders (with PII)
# to each shareholder's Stellar address balance and % ownership


import requests

searchLimitMax200 = '200'
horizonInstance = 'horizon.stellar.org'
BTissuerAddress = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM'

# With "formattingStockTestSheet.csv", use "StellarMart" as queryAsset and any numRestrictedShares
def getMergedReportForAssetWithNumRestrictedSharesUsingPIIcsvFile(queryAsset, numRestrictedShares, PIIcsvSpreadsheetFileName):
  accountBalancesFromStellar = getAccountBalancesFromStellar(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares) # for % ownership
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
  totalOutstandingShares = numRestrictedShares + numUnrestrictedShares
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
    accountStellarBlockchainPublic = lines[0]
    nameInstitution = lines[1]
    familiyName = lines[2]
    givenName = lines[3]
    dob = lines[4]
    base64encodedID = lines[5]
    addressFullStreet = lines[6]
    addressExtraInfo = lines[7]
    addressCity = lines[8]
    addressStateProvince = lines[9]
    addressPostalCode = lines[10]
    addressCountry = lines[11]
    SSN = lines[12] # tax ID
    EIN = lines[13] # tax ID type
    TIN = lines[14]
    driversLicenseNumber = lines[15]
    passportNumber = lines[16]
    otherID = lines[17]
    onboardedDate = lines[18]
    base64encodedSelfieGivenKYC = lines[19]
    email = lines[20]
    for account,balance in accountBalancesStellar: # balance is a string
      if account == accountStellarBlockchainPublic:
        balanceAsPercentOfOutstandingShares = 100 * float(balance) / totalOutstandingShares
        linkedAccounts.append((account, balance, balanceAsPercentOfOutstandingShares, nameInstitution, familiyName, givenName, dob, base64encodedID, addressFullStreet, addressExtraInfo, addressCity, addressStateProvince, addressPostalCode, addressCountry, SSN, EIN, TIN, driversLicenseNumber, passportNumber, otherID, onboardedDate, base64encodedSelfieGivenKYC, email, accountStellarBlockchainPublic))
        break
  return linkedAccounts
