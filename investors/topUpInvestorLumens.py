import sys
sys.path.append("../")
from globals import *

def topUpInvestorLumens():
  getAllInvestors # global func but change to cache reference
  availableLumensDict = getAddrsMappedToAvailableLumens(allInvestors)
  replenishTxn = replenishDepletedBalances(availableLumensDict) # impliment some kind of way to watch for misuse
  exportTxn # global
  return 1