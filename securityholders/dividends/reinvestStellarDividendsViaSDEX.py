# This is a federated reinvestment implementation, meaning Block Transfer acquires newfound equities
# on the open market in exchange for payable dividends decreed for automatic reinvestment. Security-
# holders have the option of reinvesting dividends themselves rather than in aggregate with all other
# automatic reinvestments. This may give investors marginally lower investment bases, and we generally
# reccomend this strategy for participants searching for faster reinvestment on their own time. GL.

import requests
import json
from stellar_sdk import TransactionBuilder, Network, Account

BTissuerAddress = 'GDRM3MK6KMHSYIT4E2AG2S2LWTDBJNYXE4H72C7YTTRWOWX5ZBECFWO7'
BTdistributorAddress = 'GAQKSRI4E5643UUUMJT4RWCZVLY25TBNZXDME4WLRIF5IPOLTLV7N4N6'
HorizonInstance = 'horizon.stellar.org'

def reinvestStellarUSDCdividendsToEquityViaDEX(stock, shareholdersReinvestingFilteredFromRecordDateCSV, perShareDividend, averageBulkFillPriceFINAL):
  requestAddress = 'https://' + HorizonInstance + '/accounts/' + BTdistributorAddress
  data = requests.get(requestAddress).json()
  sequenceNum = data['sequence']
  bulkTransferMax100preSegmentedXDR = TransactionBuilder(
    source_account = Account(account_id = BTdistributorAddress, sequence = int(sequenceNum)),
    network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE,
    base_fee = 100,
  )
  inFile = open(shareholdersReinvestingFilteredFromRecordDateCSV)
  readFile = inFile.read()
  readFile = readFile.strip()
  readFile = readFile.split('\n')
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
      asset_issuer = BTissuerAddress,
      amount = '{:.7f}'.format(shareholderReinvestedShares),
    )
    print( '*** Transaction added: {} reinvested ${:.2f} from dividend of ${} per share into {:.7f} new shares of stock ***\n'.format(lines[2], shareholderDividend, perShareDividend, shareholderReinvestedShares))
    
    divSum += shareholderDividend
    sharesSum += shareholderReinvestedShares
    investorSum += 1
  bulkTransferMax100preSegmentedXDR.add_text_memo('${:.2f} @ ${}'.format(divSum, averageBulkFillPriceFINAL))
  bulkTransferMax100preSegmentedXDR.set_timeout(900)
  print('\n*****\n\nTotal of ${:.2f} from dividends reinvested into {:.7f} shares at ${}/share for {} securityholders\n'.format(divSum, sharesSum, averageBulkFillPriceFINAL, investorSum))
  print('TO EXECUTE BULK TRANSFER: Sign returned message offline and broadcast to blockchain\n\n*****\n')
  return bulkTransferMax100preSegmentedXDR.build()


print(reinvestStellarUSDCdividendsToEquityViaDEX('DEMO', 'demoReinvestDividendsMSF.csv', .23, 20.1982267))
