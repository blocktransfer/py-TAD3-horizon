# - sumbmit DIV to FIRE

# - export/email(?) 8949
# different doc:
#   - interest
#     - pay all dividends via USDC for recordkeeping?
# - export DIV
#     basically just report if(fiat from BT_TREASURY to address)

# TRADE REFERENCING WALLET INSTRUCTIONS (assume open and semi-honest, as impacts your taxes)
# All trades must contain a valid memo (enough origin shares referenced to cover exit offer)
# Since atomic swaps instantly fill, you never reference syntheticIDs in a closing txn memo
# Thus, you can simplify to memo = "preExistingDataKeyPT" if len(query) > 16 else "offerID"

# OfferIDs will stay mapped to account with format offerID: {YEAR}:washSaleAdjustment until five years after the wash sale and closed (can be simple wallet wrapup)
# {"DWAC-[distributionPagingToken]": [basisPriceFromBrokerExcludedFromOriginDistribution]} stays forever
# ^ some kind of way to push out for the wallet to sign this (just check that it's only a manageDataOp in this format & signed by signers of distributor

# DWAC SERVER INSTRUCTIONS
# BT_DISTRIBUTOR sends account [numShares] stock with memo [price]||uncovered||DWAC:[coveredDate]||
# Account does manage_data( distriubtion paging_token: [assetCode]:[numShares]:[basis]:[basisDate] ) locally
#     case distributionMemo:
#       match covered (has date)    -> paging_token: [assetCode]:[numShares]:[price]:2003-6-9
#       match uncovered             -> paging_token: [assetCode]:[numShares]:uncovered:
#       match DWAC                  -> paging_token: [assetCode]:[numShares]:DWAC:[brokerDate]
#   DWAC transfers may not include the basis - brokers can send it separately in a month
#   Send user 0.0000001XLM txn w/ memo [paging_token]:[DWAC basis] so they can update
#   Currently room in memo for stocks priced under 1M/share, which should be fine
#   If becomes probalmatic, we can front truncate paging_token by a few numbers
# Use paging_token as offerID in wallet when directing closing instructions
# When selling with reference to trade, manage_data ( paging_token: [numShares - sharesSold]... )
# 
# for payments in incomingPaymentsStream:
#   try:
#     BTasset = payments["asset_issuer"] == BT_ISSUER
#   except KeyError:
#     continue
#   if(BTasset and payments["from"] == BT_DISTRIBUTOR):
#     txnAddr = payments["_links"]["transaction"]["href"]
#     txnData = requests.get(txnAddr).json()
#     try:
#       memo = txnData["memo"]
#     except KeyError:
#       memo = "42.00:2009-9-9" #tmp - testing
#       # continue
#     # distributor sends shares with memo [price]||uncovered||DWAC:[coveredDate]||
#     memo = memo.split(":")
#     basis = memo[0]
#     try:
#       historicalDate = memo[1]
#     except IndexError:
#       sys.exit(f"Failed to resolve memo {memo}")
#     assetCode = payments["asset_code"]
#     numShares = payments["amount"]
#     pagingToken = payments["paging_token"]
#     txn.append_manage_data_op(pagingToken, f"{assetCode}:{numShares}:{basis}:{historicalDate}")

# UPDATE SUCCEEDING COST BASIS FOR WASH SALE
#    - account ledger value:pair entries mapping offer ID to new basis 
#        - if(offerID in mappingItems ):
#          -  basis = offerBasis + adj.
#        - else:
#          -  basis = offerBasis
#      - requires user to publish wash sale value:pair the moment they execute the wash
#      - can remove mapping once wash sale pos. closed 
#        - must wait 30 days if sold at loss 
#        - could automatically be done in wallet background next time they login after 1mo. mark (if loss)
#          - requires computation of all open positions and potential washes when opening wallet

# WASH SALE WALLET DETAILS
#            - requires new offerID to post {succeedingOfferID: baseAdjustment<-lossDissallowedFromPriorTrade} value pair 
#            - so requires a reply from Horizon with offerID || contra lookup and then sending new txn 
#              - send the new value mapping txn with extremely high fee intentionally BEFORE displaying order confirmation to user




# affidavit to broadridge:
# If the registrant knows that securities of any class entitled to vote at a meeting are held of record by a broker, the registrant shall:the registrant shall:
# (1) equally prompt means:
#      (i) Inquire of Cede -> Brokers etc:
#                (A) Whether other persons are the beneficial owners of such securities 
#                              if so, the number of copies of the proxy and other soliciting material necessary for them
# 
# 
# 
# 
# (3) Make the inquiry required by paragraph (a)(1) of this section at least 20 business days prior to the record date of the meeting of security holders, or
# 
# 
# 
# (4) Supply, in a timely manner, each record holder and respondent bank of whom the inquiries required by paragraphs (a)(1) and (a)(2) of this section are made with copies of the proxy, other proxy soliciting material, and/or the annual report to security holders, in such quantities, assembled in such form and at such place(s), as the record holder or respondent bank may reasonably request in order to send such material to each beneficial owner of securities who is to be furnished with such material by the record holder or respondent bank; and
# 
# (5) Upon the request of any record holder or respondent bank that is supplied with proxy soliciting material and/or annual reports to security holders pursuant to paragraph (a)(4) of this section, pay its reasonable expenses for completing the sending of such material to beneficial owners.
# 
# Note 1:
# If the registrant's list of security holders indicates that some of its securities are registered in the name of a clearing agency registered pursuant to Section 17A of the Act (e.g., “Cede & Co.,” nominee for the Depository Trust Company), the registrant shall make appropriate inquiry of the clearing agency and thereafter of the participants in such clearing agency who may hold on behalf of a beneficial owner or respondent bank, and shall comply with the above paragraph with respect to any such participant (see § 240.14a-1(i)).
# Note 2:
# The attention of registrants is called to the fact that each broker, dealer, bank, association, and other entity that exercises fiduciary powers has an obligation pursuant to § 240.14b-1 and § 240.14b-2 (except as provided therein with respect to exempt employee benefit plan securities held in nominee name) and, with respect to brokers and dealers, applicable self-regulatory organization requirements to obtain and forward, within the time periods prescribed therein, (a) proxies (or in lieu thereof requests for voting instructions) and proxy soliciting materials to beneficial owners on whose behalf it holds securities, and (b) annual reports to security holders to beneficial owners on whose behalf it holds securities, unless the registrant has notified the record holder or respondent bank that it has assumed responsibility to send such material to beneficial owners whose names, addresses, and securities positions are disclosed pursuant to § 240.14b-1(b)(3) and § 240.14b-2(b)(4)(ii) and (iii).
# Note 3:
# The attention of registrants is called to the fact that registrants have an obligation, pursuant to paragraph (d) of this section, to cause proxies (or in lieu thereof requests for voting instructions), proxy soliciting material and annual reports to security holders to be furnished, in a timely manner, to beneficial owners of exempt employee benefit plan securities.
# (b) Any registrant requesting pursuant to § 240.14b-1(b)(3) or § 240.14b-2(b)(4)(ii) and (iii) a list of names, addresses and securities positions of beneficial owners of its securities who either have consented or have not objected to disclosure of such information shall:
# 
# (1) By first class mail or other equally prompt means, inquire of each record holder and each respondent bank identified to the registrant pursuant to § 240.14b-2(b)(4)(i) whether such record holder or respondent bank holds the registrant's securities on behalf of any respondent banks and, if so, the name and address of each such respondent bank;
# 
# (2) Request such list to be compiled as of a date no earlier than five business days after the date the registrant's request is received by the record holder or respondent bank; Provided, however, That if the record holder or respondent bank has informed the registrant that a designated office(s) or department(s) is to receive such requests, the request shall be made to such designated office(s) or department(s);
# 
# (3) Make such request to the following persons that hold the registrant's securities on behalf of beneficial owners: all brokers, dealers, banks, associations and other entities that exercises fiduciary powers; Provided however, such request shall not cover beneficial owners of exempt employee benefit plan securities as defined in § 240.14a-1(d)(1); and, at the option of the registrant, such request may give notice of any employee benefit plan established by an affiliate of the registrant that holds securities of the registrant that the registrant elects to treat as exempt employee benefit plan securities;
# 
# (4) Use the information furnished in response to such request exclusively for purposes of corporate communications; and
# 
# (5) Upon the request of any record holder or respondent bank to whom such request is made, pay the reasonable expenses, both direct and indirect, of providing beneficial owner information.
# 
# Note:
# A registrant will be deemed to have satisfied its obligations under paragraph (b) of this section by requesting consenting and non-objecting beneficial owner lists from a designated agent acting on behalf of the record holder or respondent bank and paying to that designated agent the reasonable expenses of providing the beneficial owner information.
# (c) A registrant, at its option, may send its annual report to security holders to the beneficial owners whose identifying information is provided by record holders and respondent banks, pursuant to § 240.14b-1(b)(3) or § 240.14b-2(b)(4)(ii) and (iii), provided that such registrant notifies the record holders and respondent banks, at the time it makes the inquiry required by paragraph (a) of this section, that the registrant will send the annual report to security holders to the beneficial owners so identified.
# 
# (d) If a registrant solicits proxies, consents or authorizations from record holders and respondent banks who hold securities on behalf of beneficial owners, the registrant shall cause proxies (or in lieu thereof requests or voting instructions), proxy soliciting material and annual reports to security holders to be furnished, in a timely manner, to beneficial owners of exempt employee benefit plan securities.
# 
# 
# 
# 
# 