import sys
sys.path.append("../../")
from globals import *

NUM_INVESTORS_EXP = 25

rawStrCapTable = """
Laylor Corp|66000000|Tammy Harris|laylorcorporation@gmail.com
Alice Lee LLC|10000000|Alana Abner|abneralana@gmail.com
BlockTrans Syndicate|5000000|John Wooten|treasury@blocktransfer.com
Just Ask For Jill|2000000|Jill Viscogliosi|justaskforjill@gmail.com
Right Way Credit Repair LLC|1500000|Felicia Dickerson|dickerson.felicia@yahoo.com
La'Tay Payne|1000000|La'Tay Payne|ladiiskylar@gmail.com
Embellish Fashion|1000000|SheYontay Hensonyonniehenson|hensonyonniehenson@gmail.com
OBBeatzz|500000|David Lengua|obbeatzz@gmail.com
Imperial Kuztom Designs LLC|500000|Tivona Champayne|tivona.champayne@gmail.com
Raekwon Anderson|500000|Raekwon Anderson|raekwonanderson2@aol.com
Jahmane Laylor|500000|Jahmane Laylor|jahmanelaylor@yahoo.com
Michael Hayles|250000|Michael Hayles|
Sadiki Anderson|250000|Sadiki Anderson|flymoneyinc@gmail.com
Makeda Anderson|250000|Makeda Anderson|kedafacemusic@gmail.com
Taliah Anari Singleton|100000|Taliah Anari Singleton|cumupnow1@gmail.com
Trey Lorenz Singleton|100000|Trey Lorenz Singleton|tlsingleton11@gmail.com
Real Yoni Pearls LLC|100000|Ivy Sagarius|
Willie Jenkins|100000|Willie Jenkins|pikefish@gmail.com
Gladys Galvez|50000|Gladys Galvez|galvezlilly486@gmail.com
Tatianna Galvez|50000|Tatianna Galvez|lillygalvez744@gmail.com
Stacey Lee|50000|Stacey Lee|humblesophistication@icloud.com
Elijah Galvez|50000|Elijah Galvez|sweetlil2933.lg@gmail.com
Daniel Galvez|50000|Daniel Galvez|sweetlil2933.lg@gmail.com
Jenira Black|50000|Jenira Black|
Chiasia White|50000|Chiasia White|
"""

def parseRawStr(rawStrCapTable):
  print("Parsing raw string")
  business_data = {}
  lines = rawStrCapTable.strip().split("\n")
  for line in lines:
    parts = line.split("|")
    registration = parts[0]
    business_data[registration] = {
      "shares": Decimal(parts[1]),
      "repName": parts[2] if parts[2] != registration else "",
      "email": parts[3]
    }
  try:
    assert(len(business_data) == len(lines) == NUM_INVESTORS_EXP)
  except AssertionError:
    sys.exit("Number of investors declared does not match number of investors imported!")
  return business_data

def printCapTable(records):
  sum = 0
  for company, data in records.items():
    shares = data["shares"]
    sum += shares
    print(f"\t\t{company}:")
    print(f"\t\t  shares: {'{:,}'.format(shares)}")
    print(f"\t\t  repName: {data['repName']}")
    print(f"\t\t  email: {data['email']}\n")
  print(f"\n\n\t\t\tTotal Shares Held: {'{:,}'.format(sum)}\n\n\n")

importedData = parseRawStr(rawStrCapTable)
printCapTable(importedData)
importAdmin = input("Verified as correct by: ")
clientCIK = "1984803"
importedAt = time.time()
fileName = f"{clientCIK} investor import at {importedAt} by {importAdmin}.txt"
with open(fileName, "w") as file:
  file.write("registration|shares|repNameForOrgOnly|email\n")
  for registration, data in importedData.items():
    file.write(f"{registration}|{data['shares']}|{data['repName']}|{data['email']}\n")
