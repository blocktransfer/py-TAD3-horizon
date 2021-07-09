import requests
import json
from pprint import pprint

def getAllAccountApplicationsFromKYC(secretKeyBlockpass):
  r = requests.get('https://kyc.blockpass.org/kyc/1.0/connect/Block_Transfer/applicants', headers = {'Authorization': secretKeyBlockpass} )
  data = r.json()
  fullDataRecords = data['data']['records']
  allKYCidentities = []
  for identities in fullDataRecords:
    recordName = identities['identities']['given_name']['value'] + ' ' + identities['identities']['family_name']['value']
    recordStatus = identities['status']
    addressDictFromStrDict = json.loads(identities['identities']['address']['value'])
    recordPhysicalAddress = addressDictFromStrDict['address'] + ', ' + addressDictFromStrDict['extraInfo'] + ', ' + addressDictFromStrDict['city'] + ', ' + addressDictFromStrDict['state'] + ' ' + addressDictFromStrDict['postalCode'] + ', ' + addressDictFromStrDict['country']
    allKYCidentities.append((recordName, recordPhysicalAddress, recordStatus))
  return allKYCidentities

def getSuccessfulCandidatesOnly(allKYCidentities):
  successfulCandidates = []
  for identities in allKYCidentities:
    if identities[2] == 'approved':
        successfulCandidates.append((identities[0], identities[1]))
  return successfulCandidates