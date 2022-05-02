import sys
sys.path.append("../")
from globals import *

def approveBulkPendingTrustlines():
  try:
    secretKey = sys.argv[1]
  except:
    print("Running without key")
  pendingAddressesWithAssetsDict = getAllPendingTrustlinesWithAsset()
  return 1
  verifiedAddressesWithAssetsDict = verifyAddressesWithAssetDict(pendingAddressesWithAssetsDict)
  signedTrustlineApprovalXDRarr = signBulkTrustlineApprovalsFromAddressAssetDict(verifiedAddressesWithAssetDict)
  exportTrustlineApprovalTransaction(signedTrustlineApprovalXDRarr)

def getAllPendingTrustlinesWithAsset():
  allAssets = getAllIssuedAssetsArr(BT_ISSUER)
  allPendingTrustlinesWithAssetArr = {}
  for assets in allAssets:
    requestAddress = "https://" + HORIZON_INST + "/accounts?asset=" + assets + ":" + BT_ISSUER + "&limit=" + MAX_SEARCH
    data = requests.get(requestAddress).json()
    blockchainRecords = data["_embedded"]["records"]
    while(blockchainRecords != []):
      for accounts in blockchainRecords:
        address = accounts["id"]
        if address in allPendingTrustlinesWithAssetArr:
          continue
        requestedAssets = []
        for assets in accounts["balances"]:
          try:
            if not assets["is_authorized"] and assets["asset_issuer"] == BT_ISSUER:
              requestedAssets.append(assets["asset_code"])
          except:
            continue
        if(requestedAssets != []):
          allPendingTrustlinesWithAssetArr[address] = requestedAssets
      # Go to next cursor
      requestAddress = data["_links"]["next"]["href"].replace("%3A", ":")
      data = requests.get(requestAddress).json()
      blockchainRecords = data["_embedded"]["records"]
  pprint(allPendingTrustlinesWithAssetArr)
  return allPendingTrustlinesWithAssetArr

def getAllIssuedAssetsArr(issuer):
  allAssets = []
  requestAddress = "https://" + HORIZON_INST + "/assets?asset_issuer=" + issuer + "&limit=" + MAX_SEARCH
  data = requests.get(requestAddress).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for entries in blockchainRecords:
      allAssets.append(entries["asset_code"])
    # Go to next cursor
    requestAddress = data["_links"]["next"]["href"].replace("\u0026", "&")
    data = requests.get(requestAddress).json()
    blockchainRecords = data["_embedded"]["records"]
  return allAssets

def getKnownAddressesFromIdentityMappingCSV(inputCSV):
  allVerifiedAddresses = []
  identityMapping = open(inputCSV, "r")
  identityMapping.readline()
  while(identityMapping.readline()):
    allVerifiedAddresses.append(identityMapping.readline().split(',')[0])
  return allVerifiedAddresses

def verifyAddressesWithAssetDict(addressesWithAssetsDict):
  allKnownShareholderAddressesList = getKnownAddressesFromIdentityMappingCSV(identityMappingCSV)
  verifiedAddressesWithAssetDict = {}
  for potentialAddress, potentialAsset in addressesWithAssetsDict: # .items() ?
    if(potentialAddress in allKnownShareholderAddressesList):
      verifiedAddressesWithAssetDict[potentialAddress] = potentialAsset
  return verifiedAddressesWithAssetDict

def signBulkTrustlineApprovalsFromAddressAssetDict(addressesWithAssetsDict):
  server = Server(horizon_url= "https://" + HORIZON_INST)
  issuer = server.load_account(account = BT_ISSUER)
  try: 
    fee = server.fetch_base_fee()
  except: 
    fee = FALLBACK_MIN_FEE
  transactions = []
  transactions.append(
    TransactionBuilder(
      source_account = issuer,
      network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
      base_fee = fee,
    )
  )
  reason = "Approve trustline: Shareholder KYC verified"
  numTxnOps, idx = 0
  for addresses, assets in addressesWithAssetsDict.items():
    transactions[idx].append_set_trust_line_flags_op(
      trustor = addresses,
      asset = Asset(assets, BT_ISSUER),
      set_flags = 1
    ) 
    numTxnOps += 1
    if(numTxnOps >= MAX_NUM_TXN_OPS):
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
      transactions[idx].sign(Keypair.from_secret(secretKey))
      numTxnOps = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = issuer,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx] = transactions[idx].add_text_memo("Approve trustline: Shareholder KYC verified").set_timeout(3600).build()
  transactions[idx].sign(Keypair.from_secret(secretKey))
  return transactions

def exportTrustlineApprovalTransaction(txnXDRarr):
  for bulkTxnXDR in txnXDRarr:
    output = open(datetime.now() + " signedApprovePendingTrustlineXDR.txt", "w")
    output.write(bulkTxnXDR)
    output.close()


approveBulkPendingTrustlines()
