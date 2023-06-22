import sys
sys.path.append("../")
from globals import *

def encodeString(str): # likely globalize under Searching
  return bytes(str, "utf-8")

testAccount = Keypair.random()

account = testAccount
signer = account.public_key
secret = account.secret

# todo: add section for company FACTAs

fullName = "First Last"
fullResidenialAddress = "99 Wall St #4640, New York, NY 10005"
taxID = "123-45-6789"
DOB = "YYYY-MM-DD"
FTIN = None

W9authStatementNoBackupWitholding = """Under penalties of perjury, I certify that:
1. The number shown on this form is my correct taxpayer identification number (or
I am waiting for a number to be issued to me); and 2. I am not subject to backup
withholding because: (a) I am exempt from backup withholding, or (b) I have not
been notified by the Internal Revenue Service (IRS) that I am subject to backup
withholding as a result of a failure to report all interest or dividends, or (c)
the IRS has notified me that I am no longer subject to backup withholding; and 3.
I am a U.S. citizen or other U.S. person (including a U.S. resident alien)."""

W9individualStatementNoBackupWitholding = f"""Under penalties of perjury, I, {fullName},
born {DOB} and residing at {fullResidenceAddress}, do hereby certify that:
1. {taxID} is my correct taxpayer identification number; and
2. I am not subject to backup withholding because:
  (a) I am exempt from backup withholding, or
  (b) I have not been notified by the Internal Revenue Service (IRS) that I am subject to
      backup withholding as a result of a failure to report all interest or dividends, or
  (c) the IRS has notified me that I am no longer subject to backup withholding; and
3. I am a U.S. citizen or other U.S. person (including a U.S. resident alien)."""

# EIN biz statement

W9authStatementWithBackupWitholding = """Under penalties of perjury, I certify that:
1. The number shown on this form is my correct taxpayer identification number (or I
am waiting for a number to be issued to me); and 2. I am currently subject to
backup withholding; and 3. I am a U.S. citizen or other U.S. person (including a
U.S. resident alien)."""

W8authStatement = """Under penalties of perjury, I declare that I have examined the
information on this form and to the best of my knowledge and belief it is true,
correct, and complete. I further certify under penalties of perjury that: - I am
the individual that is the beneficial owner (or am authorized to sign for the
individual that is the beneficial owner) of all the income or proceeds to which this
form relates or am using this form to document myself for chapter 4 purposes; - The
person named on line 1 of this form is not a U.S. person; - This form relates to:
(a) income not effectively connected with the conduct of a trade or business in the
United States; (b) income effectively connected with the conduct of a trade or
business in the United States but is not subject to tax under an applicable income
tax treaty; (c) the partner’s share of a partnership’s effectively connected taxable
income; or (d) the partner’s amount realized from the transfer of a partnership
interest subject to withholding under section 1446(f); - The person named on line 1
of this form is a resident of the treaty country listed on line 9 of the form (if
any) within the meaning of the income tax treaty between the United States and that
country; and - For broker transactions or barter exchanges, the beneficial owner is
an exempt foreign person because the person named on this form is (a) 
a nonresident alien individual or a foreign corporation, partnership, estate, or trust;
an individual who has not been, and does not plan to be, present in the United States for a total
of 183 days or more during the calendar year; and neither engaged, nor plan to be engaged
during the year, in a U.S. trade or business that has effectively connected gains from transactions with a broker or barter exchange.
Furthermore, I authorize this form to be provided to any withholding agent that has control, receipt, or
custody of the income of which I am the beneficial owner or any withholding agent
that can disburse or make payments of the income of which I am the beneficial owner.
I agree that I will submit a new form within 30 days if any certification made on
this form becomes incorrect."""

UScitizen = 1
subjectToBackupWitholding = 0

if(UScitizen):
  if(subjectToBackupWitholding):
    signature = account.sign(encodeString(W9authStatementWithBackupWitholding))
  else:
    signature = account.sign(encodeString(W9authStatementNoBackupWitholding)) # likely use Keypair.from_secret in production
else: 
  signature = account.sign(encodeString(W8authStatement))

msg = f"""signedOn: {datetime.now()}
account: {signer}
backupWitholding: {subjectToBackupWitholding}
signature: {signature}
personaSessionID: abc
instanceType: xyz""" # make sure persona session reference includes georgraphic information for signature verification incl. device type, IP info, etc.

# Send msg to Lambda

def verifySignature(attestation, publicKey): # Raises BadSignatureError
  verifierAccountView = Keypair.from_public_key(publicKey)
  return verifierAccountView.verify(encodeString(attestation), signature)

print(
  verifySignature(
    W9authStatementNoBackupWitholding,
    signer
  )
)