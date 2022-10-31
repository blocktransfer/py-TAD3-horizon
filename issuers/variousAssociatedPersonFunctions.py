import sys
sys.path.append("../")
from globals import *

def getAllAssociatedAccounts(queryAsset):
  # search docs/.WK/accounts.toml
  return 1

def getAssociatedPersonBalances(queryAsset):
  # lookup associate account holdings txns  
  
  #seach for: 
  
  # {private.affiliate}
  
  # affiliates = getAllAffiliateAccounts(queryAsset)
  # affHashmap = getAllHashedAffiliateAccounts(affiliates)
  # affBalances = dict.fromkeys(affHashmap, Decimal("0"))
  # iterate through txns:
  #  if SHA3(memo) in aff:
  #    for ppl in aff:
  #      if(SHA3 ppl == memo)
  #        if(to associate account)
  #          output[ppl] += txn[amnt]
  #        else
  #          output[ppl] -= txn[amnt]
  return 1 

def getAllHashedAffiliateAccounts(affiliates):
  return SHA3(aff) for aff in affiliates

def distributeExistingShares(asset, amount):
  # make txn from distributor src
  # create new CB op
  # claimant 1 = affiliate wallet 
  #   conditions = not(unconditional)
  # claimant 2 = lookupAffiliatedAccount(getCompanyCodeFromQueryAsset(asset))
  #   conditions = unconditional
  
  
  
  
  return 1

def grantNewRestrictedShares(asset, amount):
  return 1

def distributeVestingShares(asset, ammount, release date):
  return 1


