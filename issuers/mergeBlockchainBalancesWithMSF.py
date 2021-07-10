import requests

searchLimitMax200 = '200'
horizonInstance = 'horizon.stellar.org'
BTissuerAddress = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM'

# With "exampleMasterSecurityholderFile.csv", use "StellarMart" as queryAsset and any numRestrictedShares
def getMergedReportForAssetWithNumRestrictedSharesUsingMSF(queryAsset, numRestrictedShares, MSF):
  accountBalancesFromStellar = getAccountBalancesFromStellar(queryAsset)
  totalOutstandingShares = getTotalOutstandingShares(queryAsset, numRestrictedShares)
  isSuccessful = mergeBlockchainRecordsWithMSF(MSF, totalOutstandingShares, accountBalancesFromStellar)
  return isSuccessful

def getAccountBalancesFromStellar(queryAsset):
  accountBalancesFromStellar = []
  requestAddress = 'https://' + horizonInstance + '/accounts?asset=' + queryAsset + ':' + BTissuerAddress + '&limit=' + searchLimitMax200
  r = requests.get(requestAddress)
  data = r.json()
  blockchainRecords = data['_embedded']['records']
  while(blockchainRecords != []):
    for accounts in blockchainRecords:
      accountAddress = accounts['id']
      for balances in accounts['balances']:
        if balances['asset_type'] != 'native' and balances['asset_code'] == queryAsset:
          accountBalance = float(balances['balance'])
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
  numUnrestrictedShares = float(data['_embedded']['records'][len(data['_embedded']['records']) - 1]['total_coins'])
  totalOutstandingShares = numRestrictedShares + numUnrestrictedShares
  return totalOutstandingShares

def mergeBlockchainRecordsWithMSF(MSF, totalOutstandingShares, accountBalancesStellar):
  inFile = open(MSF)
  readFile = inFile.read()

  issuer = inFile.readline()

  readFile = readFile.strip()
  readFile = readFile.split('\n')
  inFile.close()
  linkedAccounts = []
  # rewrite first 2 headers

  try:
    issuer = issuer.split(',')
    delimiter = ','
  except:
    delimiter = '\t'

  #
  for lines in readFile[2:]:
    lines = lines.split(delimiter)
    securityholderStellarAddress = lines[0]
    sharesNotYetClaimedOnStellar = lines[1]
    for account,balance in accountBalancesStellar:
      if account == securityholderStellarAddress:
        balanceAsPercentOfOutstandingShares = 100 * float(balance) / totalOutstandingShares
        lines[0] = balance + sharesNotYetClaimedOnStellar
        break
  writeFile = open(MSF, 'w')
  writeFile = writeFile
  writeFile.close()
  return True
  

getMergedReportForAssetWithNumRestrictedSharesUsingMSF("StellarMart", 10000, "testingMasterSecurityholderFile.csv")
