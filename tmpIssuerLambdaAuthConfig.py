from globals import *

testingFuncURL = ""

# DEMO issuer keypair
pubKey = "GAZQUN6ZBXX73HMKJRYH7MXXQJ3XJS7DNBMDDBY662B47YSIRMUWYMRP"
secretKey = "SCZRDGRKSVVJFJXFZ5XZ54JKGHERCPZ5YJLDB6CQNSZP5EYIDORSQ3J2"

account = xlm.Keypair.from_secret(secretKey)

import uuid

loginQRdata = {
  "scheme": "bt-issuer/v0",
  "generatedAt": time.time(),
  "sessionNonce": str(uuid.uuid4())
}

validityToken = SHA3(
  str(loginQRdata["now"]) +
  loginQRdata["sessionNonce"]
)

# upload validityToken to Dynamo with 7 min TTL upon
# generation of QR code as value for PK sessionNonce


authToken = {
  "scheme": loginQRdata["scheme"],
  "generatedAt": loginQRdata["generatedAt"],
  "processedAt": time.time(),
  "sessionNonce": loginQRdata["sessionNonce"],
  "PK": pubKey
  "validityAuthKey": 
}

print(authToken["generatedAtTimeVerif"])

token = json.dumps(authToken)
signature = base64.b64encode(account.sign(token.encode()))

verifier = xlm.Keypair.from_public_key(json.loads(token)["PK"])
valid = verifier.verify(token.encode(), base64.b64decode(signature))

auth = {
  "token": token,
  "signature": signature.decode()
}

headers = {
  "Authorization": json.dumps(auth)
}

params = { "PKs": DEBUG_PKS }

do = 0
if(do):
  response = requests.get(
    testingFuncURL,
    headers = headers,
    params = params
  )
  print(response.text)

# Decodes to: 
serverSideToken = {
  "scheme": "bt-issuer/v0",
  "generatedAt": 1692781332.2294843,
  "processedAt": 1692781332.2295065,
  "session": "c3e20971-c902-4597-8b26-b74db188a85c",
  "PK": "GAZQUN6ZBXX73HMKJRYH7MXXQJ3XJS7DNBMDDBY662B47YSIRMUWYMRP"
}
serverSideSig = "gkYbBMBExyJr4FL9hKrMDqcah3W18tr2ao9PLbzh1cqMKZDaE7f4WKOrmr/yqKtf2LeeLp/9GF/WPy5NeDi+Cw=="


print(time.time())
time.sleep(2)
print(time.time())