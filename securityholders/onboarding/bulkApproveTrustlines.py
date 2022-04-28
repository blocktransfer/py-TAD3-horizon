import stellar ... 
import requests
import json

identityMappingCSV = "" # todo: make a style for a master identity ledger... store on offline airgapps sys with weekly? updates and sole physical backup monthly? with secure custodians (split btwn with partial images? - registered mail encrypted drives?) and then wipe Persona ea. week? on a 2-mo delayed basis? 
# that might be a bit much, and we could probably just use an authenticated sftp channel or put in Storj? 
HorizonInstance = "horizon.stellar.org"
SecretKey = "ABCD..." # Admin temporary 1-weight signers... execute on offline airgapped sys
minFeePerOp = .00001 # is there a get call for 100 stoops? 

def bulkApproveTruslines():
  r = "https://" + HorizonInstance + "..."
  data = r.json()
  
  ...
  
  # search over approved securitholder list + address mappping
  shareholder = data[...]
  while(shareholder):
    do...
    
    data = r.json()
    shareholder = data[...]
  
  # check for outsnanding trustlines requests
  
  
  # reconcile against known appproved identities
  
  
  # generate bulk approval txn XDR
  
  
  # sign and export to output.txt or (if poss.) just submit to network with minFee