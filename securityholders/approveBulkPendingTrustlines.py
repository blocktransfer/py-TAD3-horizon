import sys
sys.path.append("../")
from globals import *

try:
    SECRET = sys.argv[1]
except:
  print("Running without key")

def approveBulkPendingTrustlines():
  allPendingTrustlinesWithAssetArrDict = getAllPendingTrustlinesWithAsset()
  verifiedAddressesWithAssetArrDict = verifyAddressesWithAssetArrDict(allPendingTrustlinesWithAssetArrDict)
  signedTrustlineApprovalXDRarr = signBulkTrustlineApprovalsFromAddressAssetArrDict(verifiedAddressesWithAssetArrDict)
  exportTrustlineApprovalTransactions(signedTrustlineApprovalXDRarr)

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
  return allPendingTrustlinesWithAssetArr

def getKnownAddressesFromIdentityMappingCSV():
  allVerifiedAddresses = []
  identityMapping = open(KYC_CSV_INST)
  identityMapping.readline()
  while(identityMapping.readline()):
    allVerifiedAddresses.append(identityMapping.readline().split(',')[0])
  identityMapping.close()
  return allVerifiedAddresses

def verifyAddressesWithAssetArrDict(addressesWithAssetsArrDict):
  # TODO: Fix identity mapping schema in globals and uncomment below: 
  #allKnownShareholderAddressesList = getKnownAddressesFromIdentityMappingCSV()
  verifiedAddressesWithAssetArr = {}
  for potentialAddresses, requestedAssetArrs in addressesWithAssetsArrDict.items():
    #if(potentialAddresses in allKnownShareholderAddressesList):
    verifiedAddressesWithAssetArr[potentialAddresses] = requestedAssetArrs
  return verifiedAddressesWithAssetArr

def signBulkTrustlineApprovalsFromAddressAssetArrDict(addressesWithAssetsArrDict):
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  reason = "Known securityholder"
  numTxnOps = idx = 0
  for addresses, assetArrs in addressesWithAssetsArrDict.items():
    for assets in assetArrs:
      numTxnOps += 1
      transactions[idx].append_set_trust_line_flags_op(
        trustor = addresses,
        asset = Asset(assets, BT_ISSUER),
        set_flags = TrustLineFlags(1),
      )
      if(numTxnOps >= MAX_NUM_TXN_OPS):
        transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
        transactions[idx].sign(Keypair.from_secret(SECRET))
        numTxnOps = 0
        idx += 1
        appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
  transactions[idx].sign(Keypair.from_secret(SECRET))
  return transactions

def exportTrustlineApprovalTransactions(txnXDRarr):
  for txn in txnXDRarr:
    output = open("{} signedFreezeAssetTrustlinesXDR.txt".format(datetime.now()), "w")
    output.write(txn.to_xdr())
    output.close()

approveBulkPendingTrustlines()
