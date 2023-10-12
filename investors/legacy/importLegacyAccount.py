import sys
sys.path.append("../../")
from globals import *

FTIN_SERVER = "https://ftinmanager.blocktransfer.com"
mTLS_thing = 1 #?

def importLegacyAccounts(importTXT, legacyImportTxnHash):
  codesImported, CIK = getCodesImportedAndCIKfromLegacyImportHash(legacyImportTxnHash)
  importUnix = getDefImportUnix(legacyImportTxnHash, CIK)
  accounts = []
  with open(importTXT, "r") as finalInvestorImport:
    reader = csv.DictReader(finalInvestorImport, delimiter="|")
    for legacyInvestorData in reader:
      holdings = {
        codes: {
          "amount": legacyInvestorData.get(f"{codes}-owned"),
          "basis": legacyInvestorData.get(f"{codes}-basis", "unknown"),
          "aqAt": int(legacyInvestorData.get(f"{codes}-aqAt", importUnix)),
          **({"notes": legacyInvestorData.get(f"{codes}-notes")}
            if legacyInvestorData.get(f"{codes}-notes") else {})
        }
        for codes in codesImported if legacyInvestorData.get(f"{codes}-owned")
      }
      legalName = legacyInvestorData["legalName"]
      email = legacyInvestorData.get("email")
      FTIN = legacyInvestorData.get("FTIN")
      token = 0 if not FTIN else putFTIN({
        "FTIN": FTIN,
        "type": legacyInvestorData.get("FTIN-type")
      })
      investor = scrubNullVals({
        "PK": legalName.split(" ")[0]
        "SK": getSK(legacyInvestorData)
        "CIK": CIK,
        "FTIN": token,
        "email": email,
        "holdings": holdings,
        "legalName": legalName,
        "DOB": legacyInvestorData.get("DOB"),
        "phone": legacyInvestorData.get("phone"),
        "notes": legacyInvestorData.get("notes"),
        "addr": legacyInvestorData.get("address"),
        "mailAddr": legacyInvestorData.get("mailAddress"),
        "orgOtherContacts": legacyInvestorData.get("orgOtherContacts"),
        "orgChiefExecutive": legacyInvestorData.get("orgChiefExecutive")
      })
      
      lastName = HumanName(registration).last ### prob don't want this extra import, but infrequent call so yeah
      
      DOB = legacyInvestorData.get("DOB")
      
      investor["PK"] = 
      investor["SK"] = f"{DOB}|{legacyImportTxnHash}"
      
      accounts.append(investor)
  return accounts

def getSK(account):
  chiefIdentifier = (
    account.get("DOB") or
    account.get("email") or
    account.get("phone") or
    account.get("address") or
    f"mail/{account.get('mailAddress')}"
  )
  return f"{chiefIdentifier}|{time.time_ns()}"

def getCodesImportedAndCIKfromLegacyImportHash(legacyImportTxnHash):
  transaction = server.transactions().transaction(legacyImportOmnibusLedgerIssueTxnHash).call()
  codesImported = []
  CIKs = set()
  for legacyImportOmnibusLedgerIssueOps in transaction["operations"]:
    assert(legacyImportOmnibusLedgerIssueOps["asset_issuer"] = BT_ISSUER)
    code = legacyImportOmnibusLedgerIssueOp["asset_code"]
    codesImported.append(code)
    CIKs.add(getCIKfromCode(code))
  sameCIKs = len(CIKs) == 1
  if not sameCIKs: raise ImportError
  return codesImported, CIKs.pop()

def getDefImportUnix(legacyImportTxnHash, ledgerCIK):
  table = boto3.resource("dynamodb").Table("legacyImports")
  try:
    response = table.get_item(
      Key = {"hash": legacyImportTxnHash},
      ProjectionExpression = "received, CIK"
    )
    item = response["Item"]
    importUnix = item["received"]
    tableCIK = item["CIK"]
  except Exception:
    raise LookupError
  assert(tableCIK == ledgerCIK)
  return importUnix

def getCIKfromCode(code)
  nums = re.search(r"\d+", code)
  return int(nums.group()) if nums else 0

def scrubNullVals(dict)
  return {k: v for k, v in dict.items() if v}

def putFTIN(data):
  return requests.post(FTIN_SERVER, params=data, auth="self_").json()

# AWSdata = importLegacyAccounts("prodImports/1984803.txt", hash)
# pprint(AWSdata)
# pprint(postAWS("legacy/new", AWSdata))
