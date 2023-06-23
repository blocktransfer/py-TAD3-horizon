import sys
sys.path.append("../../")
from globals import *

# testing: print(reinvestStellarUSDCdividendsToEquityViaDEX('DEMO', 'demoReinvestDividendsMSF.csv', .23, 20.1982267))
def reinvestStellarUSDCdividendsToEquityViaDEX(stock, shareholdersReinvestingFilteredFromRecordDateCSV, perShareDividend, averageBulkFillPriceFINAL):
  bulkTransferMax100preSegmentedXDR = TransactionBuilder(
    source_account = distributor,
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = server.fetch_base_fee()*BASE_FEE_MULT,
  )
  divSum = 0
  sharesSum = 0
  investorSum = 0
  with open(shareholdersReinvestingFilteredFromRecordDateCSV) as reinvestingAccounts:
    next(reinvestingAccounts)
    for lines in reinvestingAccounts:
      lines = lines.split(',')
      shareholderDividend = float(lines[1]) * perShareDividend
      shareholderReinvestedShares = shareholderDividend / averageBulkFillPriceFINAL
      bulkTransferMax100preSegmentedXDR.append_payment_op(
        destination = lines[0],
        asset_code = stock,
        asset_issuer = getAssetIssuer(stock),
        amount = ("{:." + MAX_NUM_DECIMALS + "f}").format(shareholderReinvestedShares),
      )
      print(f"*** Transaction added: {lines[2]} reinvested ${shareholderDividend:.2f} from dividend of ${perShareDividend} per share into {shareholderReinvestedShares:.7f} new shares of stock ***\n")
      # TODO: Caution - not updated for bulk outputs
      divSum += shareholderDividend
      sharesSum += shareholderReinvestedShares
      investorSum += 1
  DRIPmemo = "${:.2f} @ ${}".format(divSum, averageBulkFillPriceFINAL)
  bulkTransferMax100preSegmentedXDR.add_text_memo(DRIPmemo).set_timeout(900).build() # update to new txn building version
  print(f"\n*****\n\nTotal of ${divSum:.2f} from dividends reinvested into {sharesSum:.7f} shares at ${averageBulkFillPriceFINAL}/share for {investorSum} securityholders\n")
  print('TO EXECUTE BULK TRANSFER: Sign returned message offline and broadcast to blockchain\n\n*****\n')
  return bulkTransferMax100preSegmentedXDR

