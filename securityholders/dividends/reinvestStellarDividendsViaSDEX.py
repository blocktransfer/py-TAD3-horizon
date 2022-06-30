import sys
sys.path.append("../../")
from globals import *

def reinvestStellarUSDCdividendsToEquityViaDEX(stock, shareholdersReinvestingFilteredFromRecordDateCSV, perShareDividend, averageBulkFillPriceFINAL):
  bulkTransferMax100preSegmentedXDR = TransactionBuilder(
    source_account = distributor
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = server.fetch_base_fee()*BASE_FEE_MULT,
  )
  inFile = open(shareholdersReinvestingFilteredFromRecordDateCSV)
  readFile = inFile.read().strip().split('\n')
  inFile.close()
  divSum = 0
  sharesSum = 0
  investorSum = 0
  for lines in readFile[1:]:
    lines = lines.split(',')
    shareholderDividend = float(lines[1]) * perShareDividend
    shareholderReinvestedShares = shareholderDividend / averageBulkFillPriceFINAL
    bulkTransferMax100preSegmentedXDR.append_payment_op(
      destination = lines[0],
      asset_code = stock,
      asset_issuer = BT_ISSUER,
      amount = '{:.7f}'.format(shareholderReinvestedShares),
    )
    print( '*** Transaction added: {} reinvested ${:.2f} from dividend of ${} per share into {:.7f} new shares of stock ***\n'.format(lines[2], shareholderDividend, perShareDividend, shareholderReinvestedShares))
    # TODO: Caution - not updated for bulk outputs
    divSum += shareholderDividend
    sharesSum += shareholderReinvestedShares
    investorSum += 1
  DRIPmemo = "${:.2f} @ ${}".format(divSum, averageBulkFillPriceFINAL)
  bulkTransferMax100preSegmentedXDR.add_text_memo(DRIPmemo).set_timeout(900).build()
  print('\n*****\n\nTotal of ${:.2f} from dividends reinvested into {:.7f} shares at ${}/share for {} securityholders\n'.format(divSum, sharesSum, averageBulkFillPriceFINAL, investorSum))
  print('TO EXECUTE BULK TRANSFER: Sign returned message offline and broadcast to blockchain\n\n*****\n')
  return bulkTransferMax100preSegmentedXDR

print(reinvestStellarUSDCdividendsToEquityViaDEX('DEMO', 'demoReinvestDividendsMSF.csv', .23, 20.1982267))
