import sys
sys.path.append("../../")
from globals import *

def importLegacyAccounts(queryAsset, importTXT):
  oldInvestorsArrOfInfoDicts = getInvestorAccountsFromLegacyTXT(queryAsset, importTXT)
  return oldInvestorsArrOfInfoDicts

def getInvestorAccountsFromLegacyTXT(queryAsset, importTXT):
  accounts = []
  with open(importTXT, "r") as file:
    reader = csv.DictReader(file, delimiter="|")
    for row in reader:
      investor = extractInvestorDataFromRow(row, queryAsset)
      investor = addInvestorDataForAWS(investor, queryAsset)
      accounts.append(investor)
  return accounts

def extractInvestorDataFromRow(row, queryAsset):
  # configure multiple assets here with queryAsset2, shares2, etc. 
  holdings = {
    queryAsset: {
      "code": queryAsset,
      "amount": row["shares"],
      "basis": row.get("basis"),
      "pending": row.get("vesting") # add pending info as needed
    }
  }
  holdings[queryAsset] = {k: v for k, v in holdings[queryAsset].items() if v}
  # could just do a 'holdings' for loop once header diction est.
  record = {
    "legalName": row["registration"],
    "DOB": row.get("DOB"),
    "address": row.get("address"),
    "email": row.get("email"),
    "phone": row.get("phone"),
    "orgRepContact": row.get("repNameForOrgOnly"),
    "holdings": holdings
  }
  return {k: v for k, v in record.items() if v}

def addInvestorDataForAWS(account, queryAsset):
  lastName = HumanName(account["legalName"]).last
  email = getItemStrStrict(account, "email")
  account["PK"] = f"{lastName}|{email}"
  DOB = getItemStrStrict(account, "DOB")
  account["SK"] = f"{DOB}|{datetime.now().isoformat()}"
  account["CIK"] = getCIKfromQueryAsset(queryAsset)
  return account

def getItemStrStrict(dict, item):
  if(dict.get(item)):
    return dict[item]
  else:
    return ""

AWSdata = importLegacyAccounts("1984803ORD", "prodImports/1984803.txt")
# pprint(AWSdata)

pprint(
  postAWS("legacy/new", AWSdata)
)
