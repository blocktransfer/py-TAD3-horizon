
# How do you want to keep record of stock splits, aside from just actually executing them? 
# Ideas:
#   - Data record in issuer account containing:
#     - Stock ticker
#     - Date of split execution/effectiveness (at 0:00:00am UTC)
#       - e.g. split on 4/20
#         - freeze trustlines at 4/20 10pm 
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
#   - Attribute in toml
#   - 
#   - 

# - sumbmit DIV to FIRE
# - export/email(?) 8949

# different doc:
#   - interest
#     - pay all dividends via USDC for recordkeeping?
# - export DIV

# basically just report if(fiat from BT_TREASURY to address)


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