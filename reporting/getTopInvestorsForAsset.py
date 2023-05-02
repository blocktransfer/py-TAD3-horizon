import sys
sys.path.append("../")
from globals import *

def getTopInvestorsForAsset(queryAsset):
  ledgerBalances = getLedgerBalances(queryAsset)
  return sorted(ledgerBalances.items(), key=lambda x:x[1])

print(getTopInvestorsForAsset("DEMO"))