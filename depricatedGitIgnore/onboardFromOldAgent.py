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
  
  ###
  
  Skip to content
Search or jump to…

Pull requests
Issues
Marketplace
Explore
 
@JFWooten4 
blocktransfer
/
stellar-interface
0
0
0
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
redundancies to internal ops
When securityholders pass KYC, they finish their application by providing their Stellar address. We then sponsor the address and its trustline with a ample lumen for thousands of transfers. If the securityholder already owns a security through an old TA, we also credit their account with said pre-existing asset on the blockchain. In the MSF (see exampleMSF in issuers), we then mark lines[1] as 0 while simultaneously inputting the actually blockchain address into lines[0]. This is the only manual transfer we ever do as detailed in MASTER_SECURITYHOLDER_FILINGS_SPECIFICATION and validated to standard STAMP identity verification levels via KYC onboarding. Done in real time as KYC applications come in from existing securityholders from old TA and not recorded on any subsidiary file.

May need to implement some of the bulk addition logic deleted here in the future when onboarding large numbers of shareholders from mega-cap books, but in general there aren't many pre-existing book-entry shareholders (and even less that even care enough to transfer book-entry shares) (say 10% existing securityholders want to transfer their shares/yr... then they juist complete nondiscriminatory KYC and have access  soon as they pass KYC onboarding, which is well within SEC-mandated turnaround times for a vast bulk of securityholders over SEC-mandated thresholds)
 main
@JFWooten4
JFWooten4 committed 40 minutes ago 
1 parent 04a4dbf commit 7d06241470f76ae041675c1d499648f28ff4e337
Showing  with 2 additions and 48 deletions.
 2  issuers/exampleMasterSecurityholderFile.csv 
@@ -1,5 +1,5 @@
Very Real Stock Inc. Shareholders,,,,,,,,,,,,,
Blockchain Address,Number of Shares From Blockchain,Registration,Email,Date of Birth / Organization,Address,Address Extra,City,State,Postal Code,Country,Onboarded Date,Issue Date of Security,Cancellation Date of Security
Blockchain Address,Number of Shares Not Yet Claimed on Blockchain,Registration,Email,Date of Birth / Organization,Address,Address Extra,City,State,Postal Code,Country,Onboarded Date,Issue Date of Security,Cancellation Date of Security
GBT5KYTYHTUORGZETT4ELIJND2ANSKNNML4ZJ3DU2N6MQPI72G5BND5Y,,Cede & Co.,real_email_for_shareholder_communication@gmx.com,1/1/1978,123 Georgia Tech Sta,350 Ferst Dr,Atlanta,GA,30332,USA,1/1/2000,,
GBUJ7ZFNCRAS5UXM4YNC4LZ5ESYIRVFQLB5BAB5FEW5AWCYU3Y7D3C2R,,Hillhouse Capital Advisors Ltd.,real_email_for_shareholder_communication@gmx.com,1/2/1978,124 Georgia Tech Sta,351 Ferst Dr,Atlanta,GA,30333,USA,1/2/2000,,
GDKN6G6VPRKJ7VJ64TI2K237RUPBKCJTYXPNZKG2RY3BZMMJX5ZMCIA4,,Morgan Stanley,real_email_for_shareholder_communication@gmx.com,1/3/1978,125 Georgia Tech Sta,352 Ferst Dr,Atlanta,GA,30334,USA,1/3/2000,,
  48  shareholders/KYConboarding.py 
  
  
  
  
@@ -22,50 +22,4 @@ def allSuccessfulCandidatesOnly(allKYCidentities):


  for identities in allKYCidentities:
    if identities[2] == 'approved':
        successfulCandidates.append((identities[0], identities[1]))
  return successfulCandidates

def mergeSuccessfulCandidatesWithOfficialStellarAddressesFromMSF(successfulCandidates, MSF):
  inFile = open(MSF)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split('\n')
  inFile.close()
  securityholders = []
  for lines in readFile[2:]:
    lines = lines.split(',')
    print(lines)
    #MSFphysicalAddress = lines[5] + ', ' + lines[6] + ', ' + + lines[7] + ', ' + lines[7] + ', ' + lines[8] + ' ' + lines[9]
    #MSFname = lines[2]
    #for identities in successfulCandidates:
    #    if MSFname == identities[0] and MSFphysicalAddress == identities[1]:
    #        securityholders.append((lines[0], identities[0], identities[1]))
    #        break
  return securityholders

def getStellarAccountsAlreadySponsored(BTissuerAddress):
  #dlsps
  return accountsAlreadySponsored

def removeExistingAccountsFromSuccessfulCandidates(successfulCandidates, accountsAlreadySponsored):
  ##
  return remainingAccountsPassedKYCyetNotSponsored

def sponsorAccountCreation(remainingAccountsPassedKYCyetNotSponsored):
  # Generate bulk ops. in groups of 100 to be signed offline and broadcast
  # to create an account / sponsor trustline
  # send 2.01 XLM # enough for 3 trustlines and 1000 transfers or 1 trustline and 150,000 transfers
  return True

def goFromKYCrequestToSponsoringAccounts(secretKeyBlockpass, BTissuerAddress):
  allKYCidentities = getAllAccountApplicationsFromKYC(secretKeyBlockpass)
  successfulCandidates = allSuccessfulCandidatesOnly(allKYCidentities)
  accountsAlreadySponsored = getStellarAccountsAlreadySponsored(BTissuerAddress)
  remainingAccountsPassedKYCyetNotSponsored = removeExistingAccountsFromSuccessfulCandidates(successfulCandidates, accountsAlreadySponsored)
  sponsorAccountCreation(remainingAccountsPassedKYCyetNotSponsored)


#pprint(getAllAccountApplicationsFromKYC('c3820f100433fb7012639110fe4136d7'))
#print("\n\n Full Attributes \n\n")
allKYCidentities = getAllAccountApplicationsFromKYC('5c1fa7cd86481dea2145d6151be0014f')
successfulCandidates = allSuccessfulCandidatesOnly(allKYCidentities)
pprint(mergeSuccessfulCandidatesWithOfficialStellarAddressesFromMSF(successfulCandidates, "testingGitIgnore.csv")) 
  return successfulCandidates 
  
  
  
1 comment on commit 7d06241
@JFWooten4
 
Member
Author
JFWooten4 commented on 7d06241 37 minutes ago
important internal KYC onboarding ops specified

@JFWooten4
 
 
Leave a comment
No file chosen
Attach files by dragging & dropping, selecting or pasting them.
 You’re receiving notifications because you commented.
© 2021 GitHub, Inc.
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
Loading complete