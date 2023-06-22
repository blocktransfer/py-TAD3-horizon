import sys
sys.path.append("../")
from globals import *
from trustlineHelper import *

validAccountPublicKeys = getValidAccountPublicKeys()

def approveBulkPendingTrustlines():
  accountsRequestingAccess = getPendingTrustlinesWithAsset()
  verifiedAccountsMappedToAssets = filterAuthorizedAccountsOnly(accountsRequestingAccess)
  signedTrustlineApprovalXDRarr = signBulkTrustlineApprovals(verifiedAccountsMappedToAssets)
  exportBulkTrustlineTransactionsXDR(signedTrustlineApprovalXDRarr)

def getPendingTrustlinesWithAsset():
  allAssets = listAllIssuerAssets()
  publicKeysMappedToRequestedAssetObjArr = {}
  for assets in allAssets:
    ledger = requestAssetAccounts(assets)
    links, records = getLinksAndRecordsFromParsedLedger(ledger)
    while(records):
      for accounts in records:
        address = accounts["id"]
        requestorAddedAlready = address in publicKeysMappedToRequestedAssetObjArr
        if(not requestorAddedAlready):
          requestedAssets = []
          for assets in accounts["balances"]:
            try:
              issuer = assets["asset_issuer"]
              if(not assets["is_authorized"] and issuer in BT_ISSUERS):
                asset = Asset(assets["asset_code"], issuer)
                requestedAssets.append(asset)
            except KeyError:
              continue
          if(requestedAssets):
            publicKeysMappedToRequestedAssetObjArr[address] = requestedAssets
      links, records = getNextLedgerData(links)
  return publicKeysMappedToRequestedAssetObjArr

def filterAuthorizedAccountsOnly(publicKeysMappedToRequestedAssetObjArr):
  verifiedPublicKeysMappedToRequestedAssetObjArr = {}
  for requestorPublicKeys, requestedAssets in publicKeysMappedToRequestedAssetObjArr.items():
    if(requestorPublicKeys in validAccountPublicKeys):
      verifiedPublicKeysMappedToRequestedAssetObjArr[requestorPublicKeys] = requestedAssets
  return verifiedPublicKeysMappedToRequestedAssetObjArr

def signBulkTrustlineApprovals(verifiedPublicKeysMappedToRequestedAssetObjArr):
  print(5)
  reason = "Known investor"
  transactions = []
  print(4)
  firstAsset = next(iter(verifiedPublicKeysMappedToRequestedAssetObjArr.values()))[0]
  print(firstAsset)
  print(type(firstAsset))
  print(3)
  issuer = getIssuerAccObj(firstAsset)
  print(2)
  issuerSigner = Keypair.from_secret(ISSUER_KEY)
  ### assume all BT_ISSUERS share a signer ###
  print(1)
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  print(0)
  numTxnOps = idx = 0
  for publicKeys, assetObjArrs in verifiedPublicKeysMappedToRequestedAssetObjArr.items():
    for assetObjs in assetObjArrs:
      transactions[idx].append_set_trust_line_flags_op(
        trustor = publicKeys,
        asset = assetObjs,
        set_flags = TrustLineFlags(1),
      )
      numTxnOps += 1
      if(numTxnOps >= MAX_NUM_TXN_OPS):
        transactions[idx] = prepTxn(transactions[idx], reason, issuerSigner)
        numTxnOps = 0
        idx += 1
        appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  transactions[idx] = prepTxn(transactions[idx], reason, issuerSigner)
  return transactions


approveBulkPendingTrustlines()
