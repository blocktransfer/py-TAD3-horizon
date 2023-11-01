import sys
sys.path.append("../../")
from globals import *

FTIN_SERVER = "https://ftinmanager.blocktransfer.com"
HORIZON_INST = "https://horizon.stellar.org"
BT_ISSUER = "GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7"
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
        "CIK": CIK,
        "FTIN": token,
        "holdings": holdings,
        "legalName": legalName,
        "addNS": time.time_ns(),
        "from": legacyImportTxnHash,
        "first": legalName.split(" ")[0],
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
  ledgerOps = requests.get(f"{HORIZON_INST}/transactions/{legacyImportTxnHash}/operations").json()
  codesImported = []
  CIKs = set()
  for issueOps in ledgerOps["_embedded"]["records"]:
    assert(issueOps["asset_issuer"] == BT_ISSUER)
    code = issueOps["asset_code"]
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

def getCIKfromCode(code):
  nums = re.search(r"\d+", code)
  return int(nums.group()) if nums else 0

def scrubNullVals(dict):
  return {key: val for key, val in dict.items() if val}

def putFTIN(data):
  return requests.post(FTIN_SERVER, params=data, auth="self_").json()

AWSdata = importLegacyAccounts("prodImports/1984803.txt", "37be2f6976bf0fc8ca9c716e49e970a2271dd6574feda80df8377530eb88b80a")
pprint(AWSdata)
# pprint(postAWS("legacy/new", AWSdata))
