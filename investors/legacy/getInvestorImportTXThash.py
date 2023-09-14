import sys
sys.path.append("../../")
from globals import *

from hashlib import sha256

def calculateSHA256(filePath):
  try:
    sha256Hash = sha256()
    with open(filePath, "rb") as file:
      while chunk := file.read(4096):
        sha256Hash.update(chunk)
    return sha256Hash.hexdigest()
  except FileNotFoundError:
    sys.exit(f"{PATH} not found.")

def sumFinalSharesHeld(filePath):
  totalShares = 0
  with open(filePath, mode="r", encoding="utf-8") as file:
    csvReader = csv.DictReader(file, delimiter='|')
    for row in csvReader:
      totalShares += Decimal(row["shares"])
  return totalShares

investorImportPath = "/mnt/d/env/stellar-interface/investors/legacy/prodImports/FILE.txt"
print(f"The SHA-256 hash of the file is: {calculateSHA256(investorImportPath)}")
print(f"You should be issuing: {sumFinalSharesHeld(investorImportPath)} shares")
