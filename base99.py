base99 = {
"00": "A", "13": "N", "26": "a", "39": "n", "52": "0", "72": "-", "92": "`","01": "B", "14": "O", "27": "b", "40": "o", "53": "1", "73": "_", "93": "~","02": "C", "15": "P", "28": "c", "41": "p", "54": "2", "74": "=", "94": " ","03": "D", "16": "Q", "29": "d", "42": "q", "55": "3", "75": "+", "95": "*DS1*","04": "E", "17": "R", "30": "e", "43": "r", "56": "4", "76": "[", "96": "*DC2*","05": "F", "18": "S", "31": "f", "44": "s", "57": "5", "77": "{", "97": "*DC3*","06": "G", "19": "T", "32": "g", "45": "t", "58": "6", "78": "]", "98": "*DC4*","07": "H", "20": "U", "33": "h", "46": "u", "59": "7", "79": "}", "99": "*ACK*","08": "I", "21": "V", "34": "i", "47": "v", "60": "8", "80": "|", "09": "J", "22": "W", "35": "j", "48": "w", "61": "9", "81": "\\","10": "K", "23": "X", "36": "k", "49": "x", "62": "!", "82": ";",
"11": "L", "24": "Y", "37": "l", "50": "y", "63": "@", "83": ":",
"12": "M", "25": "Z", "38": "m", "51": "z", "64": "#", "84": "'",
                                            "65": "$", "85": '"',
                                            "66": "%", "86": ",",
                                            "67": "^", "87": "<",           
                                            "68": "&", "88": ".",
                                            "69": "*", "89": ">",
                                            "70": "(", "90": "/",
                                            "71": ")", "91": "?", 
}

# 00 00 00 00 60 54 31 f6 1f 09 57 36 81 e0 9c 70 46 03a23d152b2c29934940779a841be56e9be115
a = []
a.append(1)

from stellar_sdk import Account, Asset, Keypair, Network, TransactionBuilder

root_keypair = Keypair.from_secret(
"SA6XHAH4GNLRWWWF6TEVEWNS44CBNFAJWHWOPZCVZOUXSQA7BOYN7XHC"
)
# Create an Account object from an address and sequence number.
root_account = Account(account=root_keypair.public_key, sequence=1)

transaction = (
 TransactionBuilder(
 source_account = root_account,
   network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
   base_fee=100,
 )
.append_payment_op( # add a payment operation to the transaction
destination="GASOCNHNNLYFNMDJYQ3XFMI7BYHIOCFW3GJEOWRPEGK2TDPGTG2E5EDW",
asset=Asset.native(),
amount="125.5",
)
.append_set_options_op( # add a set options operation to the transaction
home_domain="overcat.me"
)
.set_timeout(30)
.add_text_memo("")
.build()
)

claimableBalanceID = "00000000605431f61f09573681e09c704603a23d152b2c29934940779a841be56e9be115"
claimableBalanceID = str(int(claimableBalanceID, base=16))

c = []
for i in range(0, len(claimableBalanceID), 2):
   a = claimableBalanceID[i:i+2]
   b = a if len(a) == 2 else f"0{a}"
   c.append(base99[b])
print("".join(c))


