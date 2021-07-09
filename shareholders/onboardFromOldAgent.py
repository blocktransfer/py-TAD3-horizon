# Credit newly-onboarded Stellar accounts with assets they
# already held at any old transfer agent from the prior MSF.

import KYConboarding

def getOwnershipBalanceFromOldMSF(oldMSF):
  inFile = open(oldMSF)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split('\n')
  inFile.close()
  ownershipBalanceFromOldMSF = []
  # Logic here depends on formatting from old transfer agent
  for lines in readFile[2:]:
    lines = lines.split(',')
    shareholderFirstName = lines[999]
    shareholderFamilyName = lines[999]
    shareholderInstitutionName = lines[999]
    addressCity = lines[999]
    taxID = lines[999]
    ## Force taxID formatting to comply to xxx-xx-xxxx || xx-xxxxxxx
    if shareholderInstitutionName != "":
      tmp = taxID[2]
      taxID[2] = "-"                           # probably could optimize
      taxID = taxID.replace("-", "-" + tmp)
    else: 
      tmp1 = ... # todo well 
    if(taxID[3] == "-" and taxID[6] == "-"):
      taxIDtype = ("SSN", "ITIN") [ taxID[0] == 9 ]
    else: if(taxID[2] == "-"): ##
      taxIDtype = "EIN"
    balance = lines[999]
    notResitricted = (False, True) [ lines[999] == "Unrestricted_qualifier" ]
    ownershipBalanceFromOldMSF.append((notRestricted, balance, shareholderInstitutionName, shareholderFirstName, shareholderFamilyName, addressCity, taxID, taxIDtype))
  return ownershipBalanceFromOldMSF

def grantAssetOnStellarFromOldTAForAssetWithBalance(queryAsset, ownershipBalanceFromOldMSF):
  # open ownesgip


  redactOldMSF(paramaeters)



  #make txn to be signed open

  #log to ledger with declarative memo
  memo = 'Accout verified from old transfer agent. Granting assets.'
  # or tbh could just not do that # 
  memo_type = 'text'
  #etc


def redactOldMSF(shareholderInfo, oldTA_MSFcsv):
  #open

  # find shareholder by taxID

  #write 0 

  inFile.close()