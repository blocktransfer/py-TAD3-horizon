import sys
sys.path.append("../")
from globals import *

import nameparser

def importLegacyAccounts(queryAsset, importTXT):
  oldInvestorsArrOfInfoDicts = getInvestorAccountsFromLegacyTXT()
  return oldInvestorsArrOfInfoDicts
  postAWS("legacy/new", AWSupload)

def getInvestorAccountsFromLegacyTXT(queryAsset, importTXT):
  accounts = []
  with open(importTXT, "r") as file:
    reader = csv.DictReader(file, delimiter='|')
    for row in reader:
      investor = extractInvestorDataFromRow(row, queryAsset)
      investor = addInvestorDataForAWS(investor, queryAsset)
    accounts.append(investor)
  return accounts

def extractInvestorDataFromRow(row, queryAsset):
  return {
    "legalName": row["legalName"],
    "DOB": row["DOB"],
    "address": row["address"],
    "holdings": {
      queryAsset: {
        "amount": row["shares"],
        "basis": row["basis"],
        "available": row["vesting"]
  }

def addInvestorDataForAWS(account, queryAsset):
  lastName = HumanName(account["legalName"]).last
  account["PK"] = f"{lastName}|{account["DOB"]}"
  account["SK"] = datetime.now().isoformat()
  account["CIK"] = getCIKfromQueryAsset(queryAsset)
  return account

