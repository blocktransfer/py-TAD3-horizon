import globals..

def topUpInvestorLumens():
  getAllInvestors # global func 
  availableLumensDict = getAddrsMappedToAvailableLumens(allInvestors)
  replenishTxn = replenishDepletedBalances(availableLumensDict) # impliment some kind of way to watch for misuse
  exportTxn # global