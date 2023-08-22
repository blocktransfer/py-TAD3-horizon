from globals import *

testingFuncURL = "https://u532f7pmqkgcrae6etbp5k5tt40txsdn.lambda-url.us-east-2.on.aws/"

# DEMO issuer keypair
pubKey = "GAZQUN6ZBXX73HMKJRYH7MXXQJ3XJS7DNBMDDBY662B47YSIRMUWYMRP"
secretKey = "SCZRDGRKSVVJFJXFZ5XZ54JKGHERCPZ5YJLDB6CQNSZP5EYIDORSQ3J2"

account = Keypair.from_secret(secretKey)

import uuid

QRdata = {
  "scheme": "bt-issuer/v0",
  "now": time.time(),
  "sessionID": str(uuid.uuid4())
}

authToken = {
  "scheme": QRdata["scheme"],
  "QRtimestamp": QRdata["now"],
  "now": time.time(),
  "sessionID": QRdata["sessionID"],
  "PK": pubKey
  # "CIKs": ["  "]
}

token = json.dumps(authToken)
signature = account.sign(token.encode())

# verifier = Keypair.from_public_key(json.loads(token)["PK"])
# valid = verifier.verify(token.encode(), signature)

auth = {
  "token": token,
  "signature": signature
}

# message = base64.b64encode(json.dumps(auth).encode()).decode('utf-8')
# print(message)

response = postAWS(
  testingFuncURL,
  json.dumps({ "Authorization": token })
)



print(response)
