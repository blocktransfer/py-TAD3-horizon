# A script to listen for newly-onboarded shareholders from Blockpass,
# see if they are on the previous master securityholder file (including
# prior ownership of paper certificates)

import requests

blockpassSecretKey = 'realpassword'
BTissuerAddress = 'GD3VPKNLTLBEKRY56AQCRJ5JN426BGQEPE6OIX3DDTSEEHQRYIHIUGUM'

def getAllBlockpassAccountsFromKYCdash(blockpassSecretKey):
  #dlsps
  return

def filterOutUnsuccessfulCandidates(allBlockpassAccounts):
  #dlsps
  return successfulCandidates

def getStellarAccountsAlreadySponsored(BTissuerAddress):
  #dlsps
  return accountsAlreadySponsored

def removeExistingAccountsFromSuccessfulCandidates(successfulCandidates, accountsAlreadySponsored):
  ##
  return remainingAccountsOnboardedByBlockpassButNotSponsored

def sponsorAccountCreation(remainingAccountsOnboardedByBlockpassButNotSponsored):
  # Generate bulk ops. in groups of 100 to be signed offline and broadcast
  # to create an account / sponsor trustline
  # send 2.01 XLM # enough for 3 trustlines and 1000 transfers or 1 trustline and 150,000 transfers
  return True