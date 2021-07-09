# A script to listen for newly-onboarded shareholders from Blockpass,
# see if they are on the previous master securityholder file (including
# prior ownership of paper certificates)

import requests
from pprint import pprint

BTissuerAddress = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM'

def getAllAccountApplicationsFromKYC(secretKeyBlockpass):
  r = requests.get('https://kyc.blockpass.org/kyc/1.0/connect/Block_Transfer/applicants', headers = {'Authorization': secretKeyBlockpass} )
  data = r.json()
  fullDataRecords = data['data']['records']
  allIdentities = []
  for identities in fullDataRecords:
    recordName = identities['identities']['given_name']['value'] + ' ' + identities['identities']['family_name']['value']
    recordStatus = identities['status']
    allIdentities.append((recordName, recordStatus))
  return allIdentities

def filterOutUnsuccessfulCandidates(allBlockpassAccounts):
  #dlsps
  return successfulCandidates

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
  allBlockpassAccounts = getAllAccountApplicationsFromKYC(secretKeyBlockpass)
  successfulCandidates = filterOutUnsuccessfulCandidates(allBlockpassAccounts)
  accountsAlreadySponsored = getStellarAccountsAlreadySponsored(BTissuerAddress)
  remainingAccountsPassedKYCyetNotSponsored = removeExistingAccountsFromSuccessfulCandidates(successfulCandidates, accountsAlreadySponsored)
  sponsorAccountCreation(remainingAccountsPassedKYCyetNotSponsored)


