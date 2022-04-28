import stellar ... 
import requests
import json

SecretKey = "ABCD..." # Admin temporary 1-weight signers... execute on offline airgapped sys... then remove from Issuer 

identityMappingCSV = "" # todo: make a style for a master identity ledger... store on offline airgapps sys with weekly? updates and sole physical backup monthly? with secure custodians (split btwn with partial images? - registered mail encrypted drives?) and then wipe Persona ea. week? on a 2-mo delayed basis? 
# that might be a bit much, and we could probably just use an authenticated sftp channel or put in Storj? 
HorizonInstance = "horizon.stellar.org"
minFeePerOp = .00001 # is there a get call for 100 stoops? in case minBaseFee changes one day 
maxNumOpsPerTxn = 100
BT_issuer = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7" # check for consistency for this field against other scripts

def getKnownAddressesFromIdentityMappingCSV(inputCSV):
  KYC_known = fopen(inputCSV)
  KYC_known.readline()
  all_verified_addresses[] = ""
  i = -1
  while(KYC_known and i++):
    KYC_known = KYC_known.readline()
    all_verified_addresses[i] = inputCSV.split(',')[0]
  return all_verified_addresses

def getAllPendingTrustlinesWithAsset():
  r = "https://" + HorizonInstance + "..." + BT_issuer + "..."
  data = r.json()
  
  allPendingTrustlines = {}
  pendingTrustline = data[...]
  while(pendingTrustline):
    potentialAddress = pendingTrustline[...]
    potentialAsset = pendingTrustline[...]
    allPendingTrustlines[potentialAddress] = potentialAsset
    r = "https://" + HorizonInstance + "..." + BT_issuer + "..." -> next
    data = r.json()
    pendingTrustline = data[...]
  return allPendingTrustlines

def bulkApproveOutstandingTruslines():
  
  bulkTxnXDR = ""
  
  KYC_known = getKnownAddressesFromIdentityMappingCSV(identityMappingCSV)
  pendingTrustlinesAndAsset = getAllPendingTrustlinesWithAsset()
  
  
  
  verifiedTrustlinesToApproveWithAsset = {}
  # search over approved securitholder list + address mappping
  shareholder = data[...]
  
  i = 0
  for potentialAddress, potentialAsset in trustlinesToPotentiallyApproveWithAsset:
    if(public_address in all_verified_addresses and i < maxNumOpsPerTxn):
      trustline_approval = stellar.AuthorizeTrust(public_address, ...)
      bulkTxnXDR.append(trustline_approval) #does bulkTxnXDR need to be a list or what? 
      i++
    
    
  
  # generate bulk approval txn XDR
  
  
  # sign and export to [date, time in standard]-signedXDR-machineID-(error checking?).txt
  
  