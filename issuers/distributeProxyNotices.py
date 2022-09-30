import sys
sys.path.append("../")
from globals import *

COMPANY_ENGL_NAME = "Real Company"
MEETING_DATE = "Mar. 16, 2023"
MEETING_TIME = "9:25am Eastern Time"
ANNUAL_MEETING_YEAR = "2022"
REQUEST_DEADLINE = "Feb. 28, 2023"
FULL_OFFICE_ADDR = "1234 Maple Leaf Dr, New York, NY 12345"
AGAINST = False
TICKER = "REAL"

VOTE_FOR_LINE_1 = "1. Election of Directors"
VOTE_FOR_LINE_2 = "2. Approval of the Management Incentive Companesation Plan of 2023"
VOTE_FOR_LINE_3 = ""
VOTE_FOR_LINE_4 = "3. Business Proposition 12"
VOTE_FOR_LINE_5 = "4. Secret plan"
VOTE_FOR_LINE_6 = "5. Ratification of Selection of XXX as the Company's Independent Registered Accounting Firm"
VOTE_FOR_LINE_7 = ""
VOTE_FOR_LINE_8 = ""
VOTE_FOR_LINE_9 = ""
AGAINST_STATEMENT = "The Board of Directors recommends that you vote AGAINST the following proposals:" if AGAINST else ""
VOTE_AGAINST_LINE_1 = ""
VOTE_AGAINST_LINE_2 = ""

BT_PHONE = ""
BT_MAIL_CONTACT = "contact_sHCnJWPNWF58YDCmhX3M7a"
NOTICE_POSTCARD_FRONT = "template_vJKbiiF6Vnx8cL4H1crujS"
NOTICE_POSTCARD_BACK = "template_eb2WqQKhFje3MYrDiFP6cc"

try:
  MAIL_KEY = sys.argv[1]
except Exception:
  print("Running without mailing key")

try:
  EMAIL_KEY = sys.argv[2]
except Exception:
  print("Running without email key")

def distributeProxyNotices(queryAsset):
  sumShareholderList = getListOfAllRecordDateInvestors(queryAsset)
  sendProxyNotices(sumShareholderList)

def getOtherInvestorsFromRecordDateMSF():
  # fetch record date (queryAsset) using Open, .read().strip().split("\n") , Split; return ...
  blockchainInvestors = getRecordDateBlockchainInvestorsMappedToMSFStyle()
  investorsNotClaimed = getOtherInvestorsFromRecordDateMSF()
  
  recordDateList = []
  # open, read msf
  restricted = lines[15]
  # Assume no materials sent to restricted shareholders
  if(not restricted):
    recordDateList.append(lines)
  return recordDateList

def sendProxyNotices(queryAsset, recordDateList):
  contactIDsSent = []
  # ? toEmails = []
  for shareholders in recordDateList:
    investorData = shareholders.split("|")
    if(investorData[2]): # standardize email place in MSF
    # https://github.com/sendgrid/sendgrid-python
      toEmails.append(investorData[2])
      
      
      
      
      # time.sleep(20) ?
    else:
      contactID = getContactFromSplitLine(investorData)
      if(contactID in contactIDsSent):
        continue
      else:
        contactIDsSent.append[contactIDsSent]
      requestPostcardAddr = "https://api.postgrid.com/print-mail/v1/postcards"
      data = {"to": contactID,
        "from": BT_MAIL_CONTACT,
        "frontTemplate": NOTICE_POSTCARD_FRONT,
        "backTemplate": NOTICE_POSTCARD_BACK,
        "size": "6x4",
        "phone-num": BT_PHONE,
        "company-name-simple-engl": COMPANY_ENGL_NAME,
        "full-principal-executive-offices-for-meetings": FULL_OFFICE_ADDR,
        "request-deadline": REQUEST_DEADLINE,
        "meeting-date": MEETING_DATE,
        "meeting-time-with-time-zone": MEETING_TIME,
        "year": ANNUAL_MEETING_YEAR,
        "vote-for-line-1": VOTE_FOR_LINE_1,
        "vote-for-line-2": VOTE_FOR_LINE_2,
        "vote-for-line-3": VOTE_FOR_LINE_3,
        "vote-for-line-4": VOTE_FOR_LINE_4,
        "vote-for-line-5": VOTE_FOR_LINE_5,
        "vote-for-line-6": VOTE_FOR_LINE_6,
        "vote-for-line-7": VOTE_FOR_LINE_7,
        "vote-for-line-8": VOTE_FOR_LINE_8,
        "vote-for-line-9": VOTE_FOR_LINE_9,
        "against-statement": AGAINST_STATEMENT,
        "vote-against-line-1-cont-numbering": VOTE_AGAINST_LINE_1,
        "vote-against-line-2-cont-numbering": VOTE_AGAINST_LINE_2,
        "ticker": TICKER
      }
      requests.post(requestPostcardAddr, body=data, authorization=POSTGRID_KEY)
  # make virtual proxy notice onchain? 

def getContactFromSplitLine(investorData):
  contactGenerateAddr = "https://api.postgrid.com/print-mail/v1/contacts"
  body = {
    "firstName": investorData[1],
    "addressLine1": investorData[4],
    "addressLine2": investorData[5],
    "city": investorData[6],
    "provinceOrState": investorData[7],
    "postalOrZip": investorData[8],
    "countryCode": investorData[9]
  }
  return requests.post(contactGenerateAddr, headers=MAIL_KEY, data=body).json()["id"]

sendEmailAddr = "https://api.sendgrid.com/v3/mail/send"
authorization = { "Authorization": f"Bearer {EMAIL_KEY}", "Content-Type": "application/json" }
#print(authorization)
body = {
  "personalizations":
    [
      {
        "to":
          [
            {
              "email": "test@example.com"
            }
          ]
      }
    ],
    "from":
      {
        "email": "test@example.com"
      },
    "subject": "Sending with SendGrid is Fun",
    "content": 
      [
        {
          "type": "text/plain",
          "value": "and easy to do anywhere, even with cURL"
        }
      ]
}
t = {"personalizations": [{"to": [{"email": "test@example.com"}]}],"from": {"email": "test@example.com"},"subject": "Sending with SendGrid is Fun","content": [{"type": "text/plain", "value": "and easy to do anywhere, even with cURL"}]}
print(requests.post(sendEmailAddr, headers=authorization, json=t))