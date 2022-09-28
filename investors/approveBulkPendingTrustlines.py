import sys
sys.path.append("../")
from globals import *

validAccountPublicKeys = getValidAccountPublicKeys()

def approveBulkPendingTrustlines():
  allPendingTrustlinesMappedToAssetArr = getAllPendingTrustlinesWithAsset()
  verifiedAddressesWithAssetArrDict = verifyAddressesFromAssetDict(allPendingTrustlinesMappedToAssetArr)
  signedTrustlineApprovalXDRarr = signBulkTrustlineApprovalsFromAddressAssetArrDict(verifiedAddressesWithAssetArrDict)
  exportTrustlineApprovalTransactions(signedTrustlineApprovalXDRarr)

def getAllIssuedAssetsArr(issuer):
  allAssets = []
  requestAddress = f"https://{HORIZON_INST}/assets?asset_issuer={BT_ISSUER}&limit={MAX_SEARCH}"
  ledger = requests.get(requestAddress).json()
  while(ledger["_embedded"]["records"]):
    for entries in ledger["_embedded"]["records"]:
      allAssets.append(entries["asset_code"])
    ledger = getNextLedgerData(ledger)
  return allAssets

def getAllPendingTrustlinesWithAsset():
  allAssets = getAllIssuedAssetsArr(BT_ISSUER)
  allPendingTrustlinesWithAssetArr = {}
  for assets in allAssets:
    requestAddress = f"https://{HORIZON_INST}/accounts?asset={assets}:{BT_ISSUER}&limit={MAX_SEARCH}"
    ledger = requests.get(requestAddress).json()
    while(ledger["_embedded"]["records"]):
      for accounts in ledger["_embedded"]["records"]:
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
      ledger = getNextLedgerData(ledger)
  return allPendingTrustlinesWithAssetArr

def getKnownAddressesFromIdentityMappingCSV():
  allVerifiedAddresses = []
  identityMapping = open(MICR_CSV)
  identityMapping.readline()
  while(identityMapping.readline()):
    allVerifiedAddresses.append(identityMapping.readline().split(',')[0])
  identityMapping.close()
  return allVerifiedAddresses

def verifyAddressesFromAssetDict(addressesWithAssetsArrDict):
  verifiedAddressesMappedToAssetArr = {}
  for potentialAddresses, requestedAssetArrs in addressesWithAssetsArrDict.items():
    if(potentialAddresses in validAccountPublicKeys):
      verifiedAddressesMappedToAssetArr[potentialAddresses] = requestedAssetArrs
  return verifiedAddressesMappedToAssetArr

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
        transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
        numTxnOps = 0
        idx += 1
        appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build()
  transactions[idx].sign(Keypair.from_secret(ISSUER_KEY))
  return transactions

def exportTrustlineApprovalTransactions(txnXDRarr):
  for txn in txnXDRarr:
    output = open(f"{datetime.now()} signedFreezeAssetTrustlinesXDR.txt", "w")
    output.write(txn.to_xdr())
    output.close()

approveBulkPendingTrustlines()
