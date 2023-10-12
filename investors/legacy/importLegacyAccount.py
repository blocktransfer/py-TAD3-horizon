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
      holdings = {}
      for codes in codesImported:
        quantity = legacyInvestorData.get(f"{codes}-owned")
        if not quantity: continue
        holdings[codes] = {
          "amount": quantity,
          "basis": legacyInvestorData.get(f"{codes}-basis", "unknown"),
          "aqAt": int(legacyInvestorData.get(f"{codes}-aqAt", importUnix))
        }
        otherInfo = legacyInvestorData.get(f"{codes}-notes")
        if otherInfo: holdings[codes]["notes"] = otherInfo
      legalName = legacyInvestorData["legalName"]
      email = legacyInvestorData.get("email")
      FTIN = legacyInvestorData.get("FTIN")
      token = 0 if not FTIN else putFTIN({
        "FTIN": FTIN,
        "type": legacyInvestorData.get("FTIN-type")
      })
      investor = scrubNullVals({
        "PK": f"{getPKnameAbbrv(legalName)}|{email}"
        "SK": 
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

def getPKnameAbbrv(legalName):
  orgIdentifiers = r"\b(?:INC(?:ORPORATED)?|LLC|LTD|CO(?:-OP)?|CO(?:MPANY)?|CORP(?:ORATION)?|AG|ALLIANCE|ASSOC|CLG|CLS|CONSORTIUM|CVA|CV|CVBA|DA|DBA|DMCC|EES|EOOD|EPE|ETF|EV|FC|FCP|FDN|FOUNDATION|FUND|GP|GOV(?:ERNMENT)?|GMBH|GU|GUILD|GIE|HB|HOLDINGS|ICVC|IEC|IES|IKE|INST(?:ITUTE)?|IO|JD|JPA|JSC|KF|KG|KU|LCC|LC|LDA|LLLC|LLLP|LLP|MBH|MIC|NV|NU|NFP|NGO|NPO|OAO|ODO|OEIC|OEOD|OOD|OP|PAO|PC|PJS|PMC|PO|POA|PPO|PP|PSJC|PSC|PT|PTE|PLC|PTY|RAO|REIT|RL|RO|RA|SARL|SA|SAS|SCE|SCI|SCS|SC|SCA|SDN BHD|SE|SL|SNC|SOC(?:IETY)?|SPA|SPC|SRO|SYNDICATE|TDV|THT|TMK|TOO|TRUST|ULC|UNION|UP|VPK|WLL|ZOAO|ZOOP)(?:[.,\s;!?-]|$)"
  isAnOrg = re.search(orgIdentifiers, legalName.upper())
  if isAnOrg:
    return legalName.split(" ")[0]
  else:
    return HumanName(legalName).last

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
