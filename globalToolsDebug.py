from globals import *

def debugGetAllCurrPublicKeysForAsset(queryAsset):
  currPublicKeys = []
  ledger = requestAssetAccounts(queryAsset)
  links, records = getLinksAndRecordsFromParsedLedger(ledger)
  queryAsset = getAssetObjFromCode(queryAsset)
  while(records):
    for accounts in records:
      currPublicKeys.append(accounts["id"])
    links, records = getNextLedgerData(links)
  return currPublicKeys