import sys
sys.path.append("../")
from globals import *

validAccountPublicKeys = getValidAccountPublicKeys()

def approveBulkPendingTrustlines():
  accountsRequestingAccess = getPendingTrustlinesWithAsset()
  verifiedAddrsMappedToAssets = filterAuthorizedAccountsOnly(accountsRequestingAccess)
  signedTrustlineApprovalXDRarr = signBulkTrustlineApprovals(verifiedAddrsMappedToAssets)
  exportTrustlineApprovalTransactions(signedTrustlineApprovalXDRarr)

def getPendingTrustlinesWithAsset():
  allAssets = listAllIssuerAssets()
  pendingTrustlinesMappedToAssets = {}
  for assets in allAssets:
    requestAddress = getAssetAccountsAddress(assets)
    ledger = requests.get(requestAddress).json()
    while(ledger["_embedded"]["records"]):
      for accounts in ledger["_embedded"]["records"]:
        address = accounts["id"]
        if address in pendingTrustlinesMappedToAssets:
          continue
        requestedAssets = []
        for assets in accounts["balances"]:
          try:
            if(not assets["is_authorized"] and assets["asset_issuer"] == BT_ISSUER):
              requestedAssets.append(assets["asset_code"])
          except:
            continue
        if(requestedAssets):
          pendingTrustlinesMappedToAssets[address] = requestedAssets
      ledger = getNextLedgerData(ledger)
  return pendingTrustlinesMappedToAssets

def filterAuthorizedAccountsOnly(addressesMappedToAssets):
  verifiedAddressesMappedToAssetArr = {}
  for requesteeAddrs, requestedAssets in addressesMappedToAssets.items():
    if(requesteeAddrs in validAccountPublicKeys):
      verifiedAddressesMappedToAssetArr[requesteeAddrs] = requestedAssets
  return verifiedAddressesMappedToAssetArr

def signBulkTrustlineApprovals(addressesMappedToAssets):
  transactions = []
  appendTransactionEnvelopeToArrayWithSourceAccount(transactions, issuer)
  reason = "Known investor"
  numTxnOps = idx = 0
  for addresses, assetArrs in addressesMappedToAssets.items():
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

# todo: replace with submit to network func in global assets
def exportTrustlineApprovalTransactions(txnXDRarr):
  for txn in txnXDRarr:
    with open(f"{datetime.now()} signedFreezeAssetTrustlinesXDR.txt", "w") as output:
      output.write(txn.to_xdr())

approveBulkPendingTrustlines()
