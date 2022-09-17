# TODO: make this work with stock splits
def calculateBasisAndProceedsFromCombinedTradeData(data): 
  sharesBought = data[3] 
  # sharesBought = adjustSharesBoughtForStockSplits(data[3])
  sharesSold = data[5]
  purchaseBasis = data[4]
  saleProceeds = data[6]
  if(sharesBought == sharesSold):
    return(purchaseBasis, saleProceeds)
  elif(sharesBought > sharesSold):
    purchasePrice = sharesBought / purchaseBasis
    purchaseBasisAdj = sharesSold * purchasePrice
    return(purchaseBasisAdj, saleProceeds)
  else:
    sys.exit("tmp debug err 1")

# How do you want to keep record of stock splits, aside from just actually executing them? 
# Ideas:
#   - Data record in issuer account containing:
#     - Stock ticker
#     - Date of split execution/effectiveness (at 0:00:00am UTC)
#       - e.g. split on 4/20
#         - freeze trustlines at 4:20 10pm 
#         - execute split op.s as needed
#         - update account record to:
#           - DEMO: X to Y split on 2022-4-20
#         - the logic for adjustments would be:
#           - numBasisShares = Z
#           - read record
#           - effectiveSplitDate = splitDate + pandas.DateOffset(days = 1)
#           - for splits in readRecord
#             - if(stock == queryAsset and originTradeData["finalExecutionDate"] < effectiveSplitDate):
#               - numBasisShares = numBasisShares * X / Y
#           - return numBasisShares
#     - PROS:
#       - Likely work
#     - CONS:
#       - Messy issuer account on chain
#     - ALTERNATIVE:
#       - Put the records on the distributor account
#   - Internal record
#     - Bad; no
#   - Database of past splits on GitHub/stocks
#     - Not unlike issuer materials
#     - Given capital books are now on chain, I don't like this 
#     - Further, Cede should def. be on chain
#   - 
#   - 
#   - 
