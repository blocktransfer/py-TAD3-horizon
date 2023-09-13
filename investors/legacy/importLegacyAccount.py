import sys
sys.path.append("../../")
from globals import *

def importLegacyAccounts(queryAsset, importTXT):
  oldInvestorsArrOfInfoDicts = getInvestorAccountsFromLegacyTXT(queryAsset, importTXT)
  return oldInvestorsArrOfInfoDicts
  postAWS("legacy/new", AWSupload)

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
  return {
    "legalName": row["registration"],
    # "DOB": row["DOB"],
    # "address": row["address"],
    "email": row["email"],
    "orgRepContact": row["repNameForOrgOnly"],
    "holdings": {
      queryAsset: {
        "amount": row["shares"],
        # "basis": row["basis"],
        # "available": row["vesting"]
      }
    }
  }

def addInvestorDataForAWS(account, queryAsset):
  lastName = HumanName(account["legalName"]).last
  account["PK"] = f"{lastName}|{account['email']}"
  account["SK"] = datetime.now().isoformat()
  account["CIK"] = "1984803" #tmpBroken getCIKfromQueryAsset(queryAsset)
  return account

AWSdata = importLegacyAccounts("LAYLOR", "prodImports/LAYLOR_investor_import_2023-09-12_at_20-36_by_John_Wooten.txt")
for accounts in AWSdata:
  print(accounts["email"])