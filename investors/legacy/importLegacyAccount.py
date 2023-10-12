import sys
sys.path.append("../../")
from globals import *

HORIZON_INST = "globalizeMe!!!!!"
FTIN_SERVER = "https://ftinmanager.blocktransfer.com"
mTLS_thing = 1 #?

def importLegacyAccounts(importTXT, legacyImportTxnHash):
  legacyIssuerAssetCodes, CIK = getCodesAndCIKfromHash(legacyImportTxnHash)
  importUnix = getDefImportUnix(legacyImportTxnHash, CIK)
  accounts = []
  with open(importTXT, "r") as issuerLegacyImportFinal:
    reader = csv.DictReader(issuerLegacyImportFinal, delimiter="|")
    for legacyInvestorData in reader:
      holdings = [
        {
          "code": codes,
          "amount": legacyInvestorData.get(f"{codes}-quantity"),
          "basis": legacyInvestorData.get(f"{codes}-basis", "unknown"),
          "aqAt": int(legacyInvestorData.get(f"{codes}-aqAt", importUnix)),
          **({"notes": legacyInvestorData.get(f"{codes}-notes")}
            if legacyInvestorData.get(f"{codes}-notes") else {})
        }
        for codes in legacyIssuerAssetCodes if legacyInvestorData.get(f"{codes}-quantity")
      ]
      FTIN = legacyInvestorData.get("FTIN")
      token = 0 if not FTIN else putFTIN({
        "FTIN": FTIN,
        "type": legacyInvestorData.get("FTIN-type")
      })
      legalName = legacyInvestorData["legalName"]
      investor = scrubNullVals({
        "PK": legalName.split(" ")[0]
        "SK": getSK(legacyInvestorData)
        "CIK": CIK,
        "FTIN": token,
        "holdings": holdings,
        "legalName": legalName,
        "from": legacyImportTxnHash
        "DOB": legacyInvestorData.get("DOB"),
        "email": legacyInvestorData.get("email"),
        "phone": legacyInvestorData.get("phone"),
        "notes": legacyInvestorData.get("notes"),
        "addr": legacyInvestorData.get("address"),
        "mailAddr": legacyInvestorData.get("mailAddress"),
        "orgOtherContacts": legacyInvestorData.get("orgOtherContacts"),
        "orgChiefExecutive": legacyInvestorData.get("orgChiefExecutive")
      })
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

def getCodesAndCIKfromHash(legacyImportTxnHash):
  transaction = requests.get(f"{HORIZON_INST}/transactions/{legacyImportOmnibusLedgerIssueTxnHash}").json()
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
  return {key: val for key, val in dict.items() if val}

def putFTIN(data):
  return requests.post(FTIN_SERVER, params=data, auth="self_").json()

# AWSdata = importLegacyAccounts("prodImports/1984803.txt", hash)
# pprint(AWSdata)
# pprint(postAWS("legacy/new", AWSdata))
