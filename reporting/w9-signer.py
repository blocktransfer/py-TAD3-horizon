import sys
sys.path.append("../")
from globals import *

account = Keypair.random()

signer = account.public_key
secret = account.secret

# W9 only
# todo: add section for foreign W8 statements and sig.s / company FACTAs

authorizationStatementNoBackupWitholdingRequired = """Under penalties of perjury, I certify that:
1. The number shown on this form is my correct taxpayer identification number (or I am waiting for a number to be issued to me); and
2. I am not subject to backup withholding because: (a) I am exempt from backup withholding, or (b) I have not been notified by the Internal Revenue
Service (IRS) that I am subject to backup withholding as a result of a failure to report all interest or dividends, or (c) the IRS has notified me that I am
no longer subject to backup withholding; and
3. I am a U.S. citizen or other U.S. person (including a U.S. resident alien)."""

authorizationStatementWithBackupWitholding = """Under penalties of perjury, I certify that:
1. The number shown on this form is my correct taxpayer identification number (or I am waiting for a number to be issued to me); and
2. I am currently subject to backup withholding; and
3. I am a U.S. citizen or other U.S. person (including a U.S. resident alien)."""

def formatString(str):
  return bytes(str, "utf-8")

subjectToBackupWitholding = 0
# if(subjectToBackupWitholding):
#   // sign backup witholding
# else:
signature = account.sign(formatString(authorizationStatementNoBackupWitholdingRequired)) # likely use Keypair.from_secret in production

msg = f"""signedOn: {datetime.now()}
account: {signer}
backupWitholding: {subjectToBackupWitholding}
signature: {signature}
"""

# Send msg to Lambda

verifierAccountView = Keypair.from_public_key(signer)
# Raises error or returns None
verifierAccountView.verify(formatString(authorizationStatementNoBackupWitholdingRequired), signature)

print(msg)