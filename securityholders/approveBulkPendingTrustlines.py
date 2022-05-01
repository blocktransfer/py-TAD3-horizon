import sys
sys.path.append("../")
from globals import *

def approveBulkPendingTrustlines():
  try:
    secretKey = sys.argv[1]
  except:
    print("Running without key")
  pendingAddressesWithAssetsDict = getAllPendingTrustlinesWithAsset()
  verifiedAddressesWithAssetsDict = verifyAddressesWithAssetDict(pendingAddressesWithAssetsDict)
  signedTrustlineApprovalXDRarr = signBulkTrustlineApprovalsFromAddressAssetDict(verifiedAddressesWithAssetDict)
  exportTrustlineApprovalTransaction(signedTrustlineApprovalXDRarr)

def getAllPendingTrustlinesWithAsset():
  requestAddress = "https://" + HORIZON_INST + "..." + BT_ISSUER + "..."
  data = requests.get(requestAddress).json()
  
  allPendingTrustlines = {}
  pendingTrustline = data[...]
  while(pendingTrustline):
    potentialAddress = pendingTrustline[...]
    asset = pendingTrustline[...]

    allPendingTrustlines[potentialAddress] = asset
    requestAddress = "https://" + HORIZON_INST + "..." + BT_ISSUER + "..." -> next
    data = requests.get(requestAddress).json()
    pendingTrustline = data[...]
  return allPendingTrustlines

def getKnownAddressesFromIdentityMappingCSV(inputCSV):
  allVerifiedAddresses[] = ""
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
      transactions[idx] = transactions[idx].add_text_memo(reason).set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
      numTxnOps += 1 = 0
      idx += 1
      transactions.append(
        TransactionBuilder(
          source_account = issuer,
          network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
          base_fee = fee,
        )
      )
  transactions[idx] = transactions[idx].add_text_memo("Approve trustline: Shareholder KYC verified").set_timeout(3600).build().sign(Keypair.from_secret(secretKey))
  return transactions

def exportTrustlineApprovalTransaction(txnXDRarr):
  for bulkTxnXDR in txnXDRarr:
    output = open(datetime.now() + " signedApprovePendingTrustlineXDR.txt", "w")
    output.write(bulkTxnXDR)
    output.close()

