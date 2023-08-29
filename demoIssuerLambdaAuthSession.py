from globals import *

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from urllib.parse import urlparse, parse_qs
import uuid, qrcode

# Rotating DEMO CFO (also an unverified account)
pubKey = "GDC4LK7ZFPEHZ6JARW72XL6IIFS7YVAQZDSTQ43THYPJMZKUTGZ3JAKA"
secretKey = "SCVNEA3UKCQYHQ332QENKUINKHOTPOAADERSC6SKTUQCTD7NSH3PEXFX"
user = xlm.Keypair.from_secret(secretKey)

def main():
  QRdata = getIssuerLoginQR()
  token = getAuthTokenFromQRdata(QRdata)
  signature = base64.b64encode(
    user.sign(
      token.encode()
    )
  ).decode()
  headers = {
    "Authorization": json.dumps(
      {
        "token": token,
        "sig": signature,
        "PK": pubKey
      }
    )
  }
  testingFuncURL = ""
  if(testingFuncURL):
    response = requests.get(
      testingFuncURL,
      headers = headers
    )
    print(response.text)
  return "Auth successful"

def getIssuerLoginQR():
  issuerLoginQRdataRequestEndpoint = "https://35cj5g4b6aifmkgikxmrfvupge0rxoca.lambda-url.us-east-2.on.aws/"
  exLoginData = requests.get(issuerLoginQRdataRequestEndpoint).json()
  outputQRcode(exLoginData)
  return exLoginData

def outputQRcode(data):
  qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
  qr.add_data(data)
  qr.make()
  img = qr.make_image(fill_color="black", back_color="white")
  img.save(f"{OUT_DIR}/issuerlink_login_qr_ex_{data[19:27]}.png")

def getAuthTokenFromQRdata(data):
  parsedURL = urlparse(data)
  assert(parsedURL.scheme == "bt.issuer" and parsedURL.netloc == "link")
  inputItems = parse_qs(parsedURL.query)
  session = inputItems.get("s")[0]
  linkIP = inputItems.get("ip")[0]
  return json.dumps(
    {
      "session": session,
      "linkIP": linkIP
    }
  )
  
# raises error if invalid
def debugLocalCheckSignature(token, signature):
  # cryptography library used
  bytesToken = token.encode()
  bytesSig = base64.b64decode(signature)
  bytesPK = base64.b32decode(pubKey.encode())[1:-2]
  Ed25519PublicKey.from_public_bytes(bytesPK).verify(bytesSig, bytesToken)
  # xlm equiv
  verifier = xlm.Keypair.from_public_key(pubKey)
  verifier.verify(bytesToken, bytesSig)

print(main())

