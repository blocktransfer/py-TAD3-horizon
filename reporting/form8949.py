import sys
sys.path.append("../")
from globals import *

# TODO: Impliment some kind of caching for offerIDsMappedToChiefMemosForAccount associated with investor data

publicKey = "GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG" # testing
allOfferIDsMappedToChiefMemosForAccount = {}

# for GARLIC4DDPDXHAWNV5EBBKI7RSGGGDGEL5LH3F3N3U6I4G4WFYIN7GBG first 2500 cycles only
makerOfferIDsMappedToChiefMemos = {21223545: '_new_', 21316132: '_new_', 21351722: '_new_', 21364232: '', 21376778: '_new_', 21383538: '_new_', 22670852: '', 26036726: '_new_', 26037514: '_new_', 26039127: '_new_', 26085935: '_new_', 26933660: '', 27122387: '_new_', 27122392: '_new_', 27166814: '_new_', 27442061: '_new_', 31132828: '', 31133263: '', 31281711: '', 31283006: '', 31285519: '', 31285792: '', 31323678: '_new_', 31331230: '_new_', 32014203: '_new_', 32178754: '_new_', 32184581: '_new_', 35841027: '_new_', 36192900: '_new_', 36460176: '_new_', 36479222: '_new_', 36491640: '_new_', 37449198: '', 38828352: '', 42161017: '', 43803891: '_new_', 43846296: '_new_', 43916306: '_new_', 43946448: '_new_', 43985764: '_new_', 44014944: '_new_', 44028977: '', 44196287: '_new_', 44201965: '_new_', 44465565: '_new_', 44479534: '', 44509774: '_new_', 44541179: '_new_', 44592255: '_new_', 44620851: '_new_', 44686424: '', 44686730: '', 44687217: '', 44687296: '', 44687719: '', 44688201: '', 44688798: '', 44688961: '', 44689434: '', 44689759: '', 44693395: '', 44839482: '_new_', 44870038: '_new_', 44872418: '', 44906101: '', 44906236: '', 44938841: '_new_', 44946094: '_new_', 44949669: '', 44990128: '_new_', 44994361: '_new_', 45066043: '_new_', 45084954: '_new_', 45090060: '', 45096020: '_new_', 45098798: '_new_', 45152674: '_new_', 45155098: '_new_', 45161395: '_new_', 45165632: '_new_', 45203829: '', 45333952: '_new_', 45577437: '_new_', 45584277: '', 45692011: '_new_', 45929888: '', 45929955: '_new_', 45930097: '', 46085962: '_new_', 46158261: '_new_', 46164386: '_new_', 46332031: '_new_', 46349489: '_new_', 46523892: '_new_', 46592733: '_new_', 46680923: '_new_', 46703465: '_new_', 46809707: '_new_', 46810611: '_new_', 46918436: '_new_', 46930895: '_new_', 46940874: '_new_', 47069464: '_new_', 47284547: '_new_', 47340732: '_new_', 47391058: '_new_', 47721519: '', 47725319: '_new_', 47920863: '_new_', 48068387: '_new_', 48152420: '', 48161517: '_new_', 48200391: '_new_', 48304122: '_new_', 48467831: '_new_', 48505098: '_new_', 48540839: '_new_', 48629560: '_new_', 48629595: '_new_', 48738157: '_new_', 48754889: '_new_', 48795999: '_new_', 48843122: '', 48844457: '_new_', 48910821: '_new_', 48938101: '_new_', 49297427: '_new_', 49359587: '_new_', 49391669: '_new_', 49393450: '_new_', 49422084: '_new_', 49464231: '', 49606440: '_new_', 49666431: '_new_', 49701665: '', 49768525: '_new_', 49876170: '_new_', 50099879: '_new_', 50099951: '', 50141969: '_new_', 50149018: '_new_', 50149989: '_new_', 50456019: '_new_', 50508159: '_new_', 50529433: '_new_', 50556015: '_new_', 50576679: '', 50617631: '_new_', 50649186: '_new_', 50851681: '_new_', 50900274: '_new_', 50920330: '_new_', 50934048: '_new_', 50934825: '_new_', 50981192: '_new_', 51001304: '_new_', 51465459: '', 51465600: '_new_', 51688188: '_new_', 51732762: '_new_', 51751743: '_new_', 51751806: '_new_', 51927070: '', 52000660: '_new_', 52009517: '_new_', 52081625: '_new_', 52248080: '_new_', 52345090: '_new_', 52351417: '_new_', 52382880: '_new_', 52387113: '_new_', 52560369: '_new_', 52914301: '_new_', 53064104: '_new_', 53486305: '', 53486461: '_new_', 54100725: '_new_', 54142954: '_new_', 54375030: '_new_', 54377196: '_new_', 54384099: '_new_', 54454652: '_new_', 54490771: '', 54527895: '_new_', 54647036: '_new_', 54996033: '_new_', 55004825: '_new_', 55055407: '_new_', 55226945: '_new_', 55228320: '_new_', 55230048: '_new_', 55547408: '_new_', 55907091: '', 55957441: '_new_', 56042191: '_new_', 56063878: '_new_', 56110196: '_new_', 56113042: '_new_', 56113186: '_new_', 56507748: '_new_', 56616751: '_new_', 56645367: '_new_', 56653405: '', 56675038: '_new_', 56796571: '_new_', 57088023: '', 57381009: '_new_', 57478241: '_new_', 58127749: '', 58127784: '_new_', 58204394: '_new_', 58225709: '_new_', 58226771: '_new_', 58301049: '_new_', 58385485: '_new_', 58388438: '', 58492756: '_new_', 58564051: '_new_', 58571553: '', 58655397: '_new_', 58659177: '_new_', 58663308: '', 58871174: '_new_', 58914758: '_new_', 59169003: '_new_', 59181761: '', 59187545: '_new_', 59346936: '_new_', 59376866: '_new_', 59456005: '_new_', 59741784: '_new_', 59923462: '_new_', 59959087: '', 60810975: '_new_', 60841536: '_new_', 61143749: '', 61349348: '_new_', 61437269: '_new_', 61540717: '', 61745608: '_new_', 62038623: '_new_', 62155699: '', 62155709: '_new_', 62272792: '_new_', 63024035: '_new_', 64321822: '_new_', 65522875: '', 65522894: '_new_', 66444915: '_new_', 66600354: '_new_', 66720244: '_new_', 66720400: '_new_', 66821601: '_new_', 66870223: '_new_', 66919429: '', 67321409: '_new_', 67354625: '_new_', 67354658: '_new_', 67379987: '_new_', 67381606: '', 67442041: '_new_', 67578362: '', 67766326: '_new_', 68146474: '_new_', 68150181: '', 68898258: '_new_', 68898416: '_new_', 68918805: '_new_', 68971690: '_new_', 68975567: '_new_', 68975800: '_new_', 69890127: '_new_', 69902905: '_new_', 70036615: '', 70772916: '_new_', 70862749: '_new_', 70972453: '_new_', 70975085: '_new_', 70988515: '_new_', 71003210: '_new_', 71011636: '_new_', 71290909: '_new_', 71294230: '_new_', 71314996: '_new_', 71360002: '_new_', 71372886: '_new_', 71376592: '_new_', 71378070: '_new_', 71379854: '_new_', 71381349: '_new_', 71381760: '_new_', 71382084: '_new_', 71384424: '_new_', 71386955: '_new_', 71393793: '_new_', 71427347: '_new_', 71433029: '_new_', 71481610: '_new_', 71533668: '_new_', 71598845: '_new_', 71684491: '_new_', 71842914: '', 71872143: '_new_', 71884953: '_new_', 71974087: '_new_', 72025864: '_new_', 72026143: '_new_', 72089562: '_new_', 72097846: '', 72145948: '_new_', 72169609: '_new_', 72170079: '_new_', 72170535: '_new_', 72191789: '', 72453879: '_new_', 72508159: '_new_', 72518524: '_new_', 72521247: '', 72534225: '_new_', 72548707: '_new_', 72556479: '_new_', 72565710: '_new_', 72586063: '_new_', 72659033: '_new_', 73284849: '', 73284995: '_new_', 73297761: '_new_', 73298216: '_new_', 73339784: '_new_', 73349064: '_new_', 73469041: '', 73617291: '_new_', 73766743: '_new_', 73769576: '', 73805237: '_new_', 73839636: '_new_', 74149266: '_new_', 74233806: '_new_', 74262958: '', 74263133: '_new_', 74271615: '_new_', 74292440: '_new_', 74300808: '_new_', 74325017: '', 74424414: '_new_', 74559030: '_new_', 74660547: '_new_', 74661573: '_new_', 74766716: '_new_', 74811666: '_new_', 75180729: '', 75180874: '_new_', 75416251: '_new_', 75420928: '_new_', 75423126: '', 75444223: '_new_', 75489083: '_new_', 75495653: '_new_', 75554522: '_new_', 75632642: '_new_', 75634206: '', 75686692: '_new_', 75799264: '_new_', 75822198: '_new_', 75872037: '_new_', 75925084: '_new_', 75976813: '', 76039169: '_new_', 76040917: '_new_', 76170293: '_new_', 76176704: '_new_', 76259596: '_new_', 76260677: '_new_', 76445110: '', 76518417: '_new_', 76621593: '', 76660547: '_new_', 76661045: '_new_', 76661369: '_new_', 76682643: '_new_', 76682951: '_new_', 76695335: '', 76752773: '_new_', 76832096: '', 77079170: '_new_', 77144481: '_new_', 77222758: '', 77413425: '_new_', 77448551: '_new_', 77476993: '_new_', 77540460: '_new_', 77571581: '_new_', 77749446: '_new_', 77750329: '_new_', 77819282: '_new_', 77829018: '_new_', 78103909: '', 78408204: '_new_', 78408207: '', 78498270: '_new_', 80025915: '_new_', 80027306: '_new_', 80028145: '', 80031725: '_new_', 80256413: '', 80363287: '', 80439992: '_new_', 80588698: '_new_', 80763311: '_new_', 80820770: '_new_', 80840468: '_new_', 81289362: '_new_', 81326389: '', 81347315: '_new_', 82003010: '_new_', 82003014: '', 82240888: '_new_', 82277319: '_new_', 82665729: '', 82815139: '_new_', 82825356: '_new_', 83374903: '_new_', 83431622: '', 83471138: '_new_', 83474988: '_new_', 83491817: '', 83749337: '_new_', 83786721: '_new_', 83921645: '', 83953679: '_new_', 83954150: '_new_', 83966277: '', 83966498: '', 83982174: '_new_', 84035864: '_new_', 84135322: '_new_', 84179719: '', 84574767: '_new_', 84742007: '_new_', 84822258: '', 84920148: '_new_', 85232251: '', 85232397: '_new_', 85236647: '_new_', 85304656: '', 85304659: '_new_', 85470982: '_new_', 85521581: '_new_', 86079614: '', 86079760: '_new_', 86334916: '_new_', 86583761: '_new_', 86645720: '', 86692512: '_new_', 87544505: '_new_', 87559676: '', 87576201: '_new_', 87657594: '_new_', 87765041: '_new_', 87892388: '_new_', 87892497: '_new_', 87892685: '_new_', 87893851: '_new_', 87941387: '_new_', 87941547: '_new_', 88241989: '', 88242159: '_new_', 88483946: '_new_', 88497793: '_new_', 88497948: '_new_', 88542176: '_new_', 88567915: '_new_', 88581920: '_new_', 88613209: '_new_', 88631238: '_new_', 88638781: '_new_', 88640786: '_new_', 88692452: '', 88692594: '_new_', 88757251: '_new_', 88972498: '_new_', 88972972: '_new_', 89070946: '_new_', 89079043: '', 89324893: '_new_', 89327410: '_new_', 90079903: '_new_', 90085877: '_new_', 90106646: '_new_', 90107485: '_new_', 90124461: '_new_', 90316870: '_new_', 90317795: '_new_', 90330244: '_new_', 90985199: '_new_', 91322476: '_new_', 91340952: '', 91340970: '_new_', 91415005: '_new_', 91601223: '_new_', 91606592: '_new_', 91653296: '_new_', 91731585: '_new_', 92888332: '_new_', 94455348: '_new_', 94456764: '_new_', 94476093: '_new_', 94476942: '_new_', 94550921: '_new_', 94631915: '_new_', 94660834: '_new_', 95379808: '_new_', 95449687: '_new_', 95582883: '_new_', 95586862: '_new_', 95588873: '_new_', 95864011: '_new_', 95954864: '_new_', 96227530: '', 96227678: '_new_', 96346577: '_new_', 96786060: '_new_', 96958913: '', 97140809: '_new_', 97265653: '_new_', 97363443: '', 97912116: '_new_', 98172758: '_new_', 98866527: '_new_', 99113362: '_new_', 99121270: '_new_', 99123280: '_new_', 99123530: '_new_', 99130723: '_new_', 99136162: '_new_', 99154776: '_new_', 100854324: '_new_', 100854643: '', 100907438: '_new_', 101615837: '_new_', 101637217: '_new_', 101887566: '_new_', 101922775: '_new_', 102065134: '_new_', 102068231: '', 102097990: '_new_', 102132659: '_new_', 102546472: '_new_', 102635956: '_new_', 103198439: '', 103198527: '_new_', 103460980: '_new_', 103500359: '_new_', 103587934: '', 103857715: '_new_', 103937952: '_new_', 103939191: '_new_', 104187194: '_new_', 104275989: '', 105286965: '_new_', 105515565: '_new_', 105565257: '_new_', 105598696: '_new_', 105601485: '_new_', 107121730: '_new_', 107484925: '_new_', 107485783: '_new_', 107550010: '_new_', 109878138: '_new_', 110422019: '_new_', 110847617: '_new_', 111008470: '_new_', 111640280: '_new_', 111662168: '', 111856216: '_new_', 112254060: '_new_', 112257580: '_new_', 112591112: '_new_', 113312272: '_new_', 113330676: '_new_', 113330933: '', 113837904: '_new_', 114267749: '_new_', 114267880: '', 114351920: '_new_', 114377073: '_new_', 114432077: '_new_', 114438707: '', 114693525: '_new_', 115315185: '', 115315201: '_new_', 115375497: '_new_', 115379050: '_new_', 115393295: '_new_', 115640270: '_new_', 115693298: '_new_', 115693414: '', 115697348: '_new_', 115698736: '_new_', 115698745: '', 115711356: '_new_', 115716335: '_new_', 115722922: '', 115726839: '_new_', 115826631: '_new_', 115827915: '_new_', 115862967: '_new_', 115868595: '_new_', 115921282: '_new_', 115941425: '_new_', 115955463: '_new_', 115962280: '_new_', 115973285: '_new_', 116399364: '_new_', 116404552: '_new_', 116463690: '_new_', 116463817: '', 116502100: '_new_', 116517767: '_new_', 116560272: '_new_', 116784100: '_new_', 117632558: '', 117632574: '_new_', 117684597: '_new_', 118371053: '_new_', 118492528: '_new_', 118498422: '_new_', 118927632: '', 118927768: '_new_', 119878465: '_new_', 121065664: '', 121065827: '_new_', 121412707: '_new_', 121920946: '_new_', 121931568: '_new_', 121946618: '_new_', 122065840: '_new_', 122805227: '_new_', 122825249: '', 122867725: '_new_', 124289252: '', 124619725: '_new_', 125850963: '', 125851137: '_new_', 126489946: '_new_', 126903013: '_new_', 126948693: '', 127120233: '_new_', 127271186: '_new_', 127281691: '_new_', 129094402: '_new_', 129095110: '', 129191695: '_new_', 129285981: '_new_', 129343096: '_new_', 129420831: '_new_', 129429384: '_new_', 129437262: '', 129544040: '_new_', 129573168: '_new_', 129606914: '', 129633980: '_new_', 129944796: '_new_', 129980381: '', 130176908: '_new_', 130405008: '_new_', 131252480: '_new_', 131418947: '_new_', 131690259: '_new_', 131748257: '', 131950532: '_new_', 131965335: '_new_', 132152878: '', 132512003: '_new_', 132961499: '_new_', 133225781: '', 133765466: '_new_', 134210293: '_new_', 134246388: '_new_', 134277388: '', 134387893: '_new_', 134738903: '_new_', 134830990: '_new_', 134836710: '_new_', 135073750: '_new_', 135172489: '_new_', 135209842: '', 135548378: '_new_', 135646912: '_new_', 135682471: '', 136330161: '_new_', 137017369: '_new_', 137018587: '_new_', 137315704: '_new_', 137330526: '', 138701392: '_new_', 139114409: '_new_', 139140266: '_new_', 140052113: '_new_', 140074131: '_new_', 140560238: '_new_', 140730944: '', 140890962: '_new_', 140891403: '_new_', 141691572: '_new_', 142479372: '', 143313017: '_new_', 143397842: '_new_', 144082707: '_new_', 145039956: '_new_', 145040140: '', 145100912: '_new_', 145144493: '_new_', 145301771: '_new_', 146838598: '', 146838684: '_new_', 147068483: '_new_', 147069130: '_new_', 147795711: '_new_', 148252215: '', 148252294: '_new_', 148420329: '_new_', 148451393: '_new_', 148452133: '_new_', 148453503: '_new_', 148455043: '_new_', 148595483: '_new_', 148780616: '_new_', 148873659: '_new_', 148933296: '_new_', 148936547: '', 149759695: '_new_', 149925416: '_new_', 150584762: '', 150850006: '_new_', 150851678: '_new_', 150996249: '_new_', 151688862: '_new_', 154323973: '', 154358435: '', 154500301: '_new_', 154546770: '_new_', 154566942: '_new_', 154697705: '_new_', 155284888: '_new_', 155352407: '_new_', 155378332: '_new_', 155450486: '_new_', 155568330: '', 155568601: '_new_', 155586148: '_new_', 155676049: '_new_', 155751330: '_new_', 155973356: '_new_', 156164536: '_new_', 156414010: '_new_', 156526113: '_new_', 156716033: '_new_', 156748805: '', 156847004: '_new_', 157210916: '_new_', 157228022: '_new_', 157292878: '', 157569026: '_new_', 157740684: '_new_', 157792224: '_new_', 157795338: '_new_', 157803748: '_new_', 157848090: '_new_', 158039982: '_new_', 158138533: '_new_', 158240593: '_new_', 158481110: '_new_', 158679491: '_new_', 159073581: '_new_', 159320455: '_new_', 159403907: '', 159404267: '_new_', 159668571: '_new_', 159947946: '_new_', 160137486: '_new_', 160253849: '_new_', 160393129: '_new_', 160625346: '_new_', 160881591: '_new_', 160911281: '_new_', 161212590: '_new_', 161238416: '_new_', 161478734: '_new_', 161521969: '_new_', 161579570: '_new_', 161636561: '_new_', 162030267: '_new_', 162049138: '', 162326957: '_new_', 162570267: '_new_', 162965901: '_new_', 163891730: '', 163891955: '_new_', 163893028: '_new_', 163898667: '_new_', 163899934: '_new_', 163911476: '_new_', 163916703: '_new_', 163917696: '_new_', 163917781: '_new_', 163917841: '', 163917903: '_new_', 163921717: '_new_', 164433997: '_new_', 164439867: '_new_', 164473910: '_new_', 164474079: '', 164490155: '_new_', 164492560: '_new_', 164509863: '', 164515968: '_new_', 165000771: '_new_', 165003373: '', 165007532: '_new_', 165009124: '_new_', 165013601: '_new_', 165016566: '_new_', 165017762: '_new_', 165028378: '_new_', 165054234: '_new_', 165276246: '_new_', 165300262: '', 165398696: '_new_', 165644080: '_new_', 165733457: '_new_', 165763479: '_new_', 165859387: '_new_', 165860324: '_new_', 165861335: '', 165910052: '_new_', 165945893: '_new_', 165961978: '_new_', 165972733: '_new_', 166036585: '', 166060323: '_new_', 166062148: '_new_', 166138648: '_new_', 167149059: '_new_', 167150344: '_new_', 167421786: '_new_', 167881540: '_new_', 167904335: '_new_', 167904513: '_new_', 167909913: '', 167910095: '_new_', 167911005: '_new_', 167911172: '_new_', 168043873: '_new_', 168811444: '_new_', 168907514: '_new_', 168907804: '', 170178391: '', 170989764: '_new_', 171918067: '_new_', 171925279: '_new_', 172318832: '_new_', 172703776: '_new_', 172919020: '_new_', 172985545: '', 173014573: '_new_', 173650573: '_new_', 173762547: '_new_', 174217243: '', 174720681: '_new_', 175401500: '_new_', 175759346: '', 175759709: '_new_', 175788163: '_new_', 175947580: '_new_', 176218956: '_new_', 176272739: '_new_', 177269305: '_new_', 177359024: '_new_', 178020985: '_new_', 178183858: '_new_', 178585065: '_new_', 179134995: '', 179612123: '_new_', 179630009: '_new_', 179632720: '_new_', 179646978: '_new_', 179661326: '_new_', 180129400: '_new_', 180132152: '_new_', 180180294: '_new_', 182149752: '_new_', 182150270: '', 182676347: '_new_', 183920709: '_new_', 185827085: '_new_', 185827618: '_new_', 185827848: '_new_', 185829132: '', 185829814: '_new_', 186464518: '_new_', 186468189: '_new_', 187069827: '', 188919458: '_new_', 189207472: '_new_', 189339422: '', 189781499: '_new_', 189997660: '_new_', 190106323: '_new_', 190237488: '', 190243210: '_new_', 190243423: '_new_', 190755282: '_new_', 191106207: '_new_', 193187342: '_new_', 194021099: '_new_', 194578070: '_new_', 194839566: '_new_', 194839792: '_new_', 194909802: '_new_', 194912047: '_new_', 197229047: '', 197231302: '', 197234655: '_new_', 197234906: '_new_', 197524446: '_new_', 197525040: '_new_', 197558341: '_new_', 197558539: '_new_', 199803922: '_new_', 200173928: '_new_', 200454393: '_new_', 201078803: '', 201081163: '', 201563136: '_new_', 201818717: '_new_', 202381426: '_new_', 202424689: '_new_', 203190416: '_new_', 203190626: '_new_', 203697782: '_new_', 203831522: '_new_', 203831715: '_new_', 203835025: '_new_', 203835255: '_new_', 206043312: '_new_', 206703087: '_new_', 207677996: '_new_', 209759518: '_new_', 209864931: '_new_', 210171732: '_new_', 210343190: '_new_', 210343354: '_new_', 210570649: '', 210571001: '_new_', 210688713: '', 210689142: '_new_', 210872532: '_new_', 211402255: '_new_', 211880240: '_new_', 211919907: '_new_', 211920133: '_new_', 212473524: '_new_', 212535343: '_new_', 212813646: '_new_', 215133802: '_new_sell_', 215133807: '_new_sell_', 219348478: '_new_sell_', 219348968: '_new_sell_', 219348986: '_new_sell_', 219351377: '', 219576062: '_new_sell_', 219858093: '_new_sell_', 219875324: '_new_sell_', 219900825: '_new_sell_', 220365160: '_new_sell_', 220440472: '_new_sell_', 221937360: '_new_sell_', 221994821: '_new_sell_', 222628641: '_new_sell_', 222668419: '_new_sell_', 222860457: '_new_sell_', 223180365: '_new_sell_', 223230625: '_new_sell_', 223272460: '_new_sell_', 223497339: '_new_sell_', 224197534: '_new_sell_', 225572477: '_new_sell_', 225973215: '_new_sell_', 226028658: '_new_sell_', 227230548: '_new_sell_', 227231152: '_new_sell_', 227231885: '_new_sell_', 227233849: '_new_sell_', 227233878: '_new_sell_', 227388166: '_new_sell_', 227789239: '_new_sell_', 228268906: '_new_sell_', 228289785: '_new_sell_', 228877286: '_new_sell_', 229539946: '_new_sell_', 229540126: '_new_sell_', 231727433: '_new_sell_', 232221804: '_new_sell_', 232228616: '_new_sell_', 232248317: '_new_sell_', 232742212: '_new_sell_', 232742352: '_new_sell_', 233979524: '_new_sell_', 234708456: '', 234708680: '_new_sell_', 235817114: '_new_sell_', 235885328: '_new_sell_', 235929318: '_new_sell_', 236905272: '_new_sell_', 238521504: '_new_sell_', 238521510: '_new_sell_', 238894315: '_new_sell_', 239457015: '_new_sell_', 239544554: '', 240042447: '_new_sell_', 240322924: '_new_sell_', 240980083: '_new_sell_', 241335046: '', 242058041: '_new_sell_', 242058228: '_new_sell_', 242922130: '_new_sell_', 243198976: '_new_sell_', 243281813: '', 243807691: '_new_sell_', 244027818: '_new_sell_', 244051538: '_new_sell_', 245018251: '_new_sell_', 246238222: '_new_sell_', 246743697: '_new_sell_', 246877692: '_new_sell_', 247232213: '', 247860882: '_new_sell_', 248442757: '_new_sell_', 248447926: '_new_sell_', 248634416: '_new_sell_', 249326153: '', 255824483: '_new_sell_', 256598282: '_new_sell_', 256598294: '_new_sell_', 256625409: '_new_sell_', 256625473: '_new_sell_', 256634689: '_new_sell_', 256634715: '_new_sell_', 256679291: '_new_sell_', 256679314: '_new_sell_', 256687185: '_new_sell_', 256687259: '_new_sell_', 257305756: '_new_sell_', 257305813: '_new_sell_', 257448074: '', 257448391: '_new_sell_', 257554814: '_new_sell_', 258114291: '_new_sell_', 258167317: '_new_sell_', 258472607: '_new_sell_', 258757173: '_new_sell_', 260056992: '_new_sell_', 260158062: '_new_sell_', 260656594: '', 260702952: '_new_sell_', 262290660: '', 262290872: '_new_sell_', 262512654: '_new_sell_', 264892808: '_new_sell_', 265163552: '', 265324686: '_new_sell_', 265327628: '_new_sell_', 265453776: '_new_sell_', 265460640: '_new_sell_', 265773939: '_new_sell_', 266098659: '', 266690956: '_new_sell_', 267104437: '_new_sell_', 267407578: '_new_sell_', 267948774: '_new_sell_', 268043738: '_new_sell_', 268393158: '_new_sell_', 270507253: '_new_sell_', 270647093: '_new_sell_', 271926296: '_new_sell_', 272477619: '_new_sell_', 273596421: '_new_sell_', 274683141: '_new_sell_', 275676848: '_new_sell_', 276965964: '_new_sell_', 277118053: '', 277590842: '_new_sell_', 278187837: '_new_sell_', 278529813: '', 279173466: '_new_sell_', 279199719: '_new_sell_', 279302880: '_new_sell_', 279419268: '_new_sell_', 279678929: '_new_sell_'}

# for BT_ISSUER
#makerOfferIDsMappedToChiefMemos = {795997347: '', 805012105: '', 808077587: '', 814060465: '', 845029809: '', 850277083: '', 862213103: '', 888731543: '', 896978373: '', 933047668: '', 933645028: '', 935618893: '', 959478679: '', 960204279: '', 960205486: '', 961221601: '', 961226194: '', 961231550: '', 962903771: '', 962905566: '', 962909989: '', 962917171: '', 963002397: '', 963002518: '', 963379783: '', 963380201: '', 963520213: '', 963887543: '', 963914453: '', 964092582: '', 967336354: '', 967336673: '', 967337584: '', 967952647: '', 968609686: '', 968995036: '', 969293250: '', 969296973: '', 969697185: '', 970530708: '', 970614837: '', 975631159: '', 975632612: '', 975644902: '', 976302501: '', 977042627: '', 977215102: '', 977684556: '', 977824164: '', 977935244: '', 977963836: '', 978188716: '', 978194427: '', 978488137: '', 978555798: '', 978929845: '', 979301289: '', 979613342: '', 981099167: '', 981208236: '', 981465307: '', 981795672: '', 981865107: '', 982232285: '', 982232720: '', 982272940: '', 982273054: '', 982273477: '', 982275115: '', 982329539: '', 982340356: '', 982374567: '', 982374691: '', 982812073: '', 982947485: '', 982947952: '', 983199144: '', 983234375: '', 983299066: '', 983395217: '', 983442905: '', 983443195: '', 983443693: '', 983455021: '', 983750669: '', 983750862: '', 983937930: '', 983943173: '', 983943489: '', 984039889: '', 984064396: '', 984461665: '', 984465687: '', 984536491: '', 984553351: '', 984563945: '', 984777551: '', 984778955: '', 985673104: '', 985783035: '', 985943136: '', 986043102: '', 986332433: '', 986335337: '', 986414577: '', 986449091: '', 986452854: '', 986466719: '', 986502988: '', 986523438: '', 986632366: '', 987046331: '', 987050785: '', 987148579: '', 987411901: '', 987733948: '', 987767409: '', 987893596: '', 987895059: '', 987895866: '', 988002985: '', 988024328: '', 988169058: '', 996195363: '', 996225627: '', 996585646: '', 996608352: '', 996830672: '', 997089267: '', 997149016: '', 997218055: '', 997845991: ''}

lastYear = datetime.today().year - 1
taxYearStart = pandas.to_datetime(f"{lastYear}-01-01T00:00:00Z") # modify here for fiscal years
taxYearEnd = taxYearStart + pandas.DateOffset(years = 1) # set custom taxYearEnd for 52-53 week

def form8949forAccount():
  # getAllOfferIDsMappedToChiefMemosForAccount(publicKey)
  (buyOfferIDsMappedToCostBasis, sellOfferIDsMappedToProceeds) = getTradesWithBasisOrProceedsFromOfferID()
  calculateYearlyPNL(publicKey)

# get lot sale instr. from memo using offerID txns
# -- full takes = easy memo id from op
# -- makes = shows other guy SO we need the original sell offer txn obj

# FIELD NEEDED:
# Description of property
# Date acquired
# Date sold
# Proceeds
# Basis
# Adjustment/wash sale
# PNL

# - assume prior calendar year
def calculateTaxYearPNL():
  # figure out which offer IDs where sales this tax year 
  getTradesWithBasisOrProceedsFromOfferID
  
  
  
  
  
  offerIDsMappedToProceeds = {}
  
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/trades?limit={MAX_SEARCH}"
  #print(requestAddr)
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  lastOfferID = totalProceeds = 0
  while(blockchainRecords != []):
    #print(requestAddr)
    proceeds = 3000000
    cost = 10
    for trades in blockchainRecords:
      
      
      opID = trades["id"].split("-")[0]

      settlementTime = trades["ledger_close_time"]

      baseOfferID = trades["base_offer_id"]
      baseAddr = trades["base_account"]
      baseAmount = trades["base_amount"]
      try:
        baseAsset = Asset(trades["base_asset_code"], trades["base_asset_issuer"])
      except KeyError:
        baseAsset = Asset.native()
      
      counterOfferID = trades["counter_offer_id"]
      counterAddr = trades["counter_account"]
      counterAmount = trades["counter_amount"]
      
      try:
        counterAsset = Asset(trades["counter_asset_code"], trades["counter_asset_issuer"])
      except KeyError:
        counterAsset = Asset.native()
      
      investorOfferID = baseOfferID if baseAddr == publicKey else counterOfferID
      if(investorOfferID == lastOfferID):
        totalProceeds += proceeds
        totalCost += cost
      else:
        if(not totalProceeds):
          totalProceeds = proceeds
          totalCost = cost
        else:
          offerIDsMappedToProceeds[lastOfferID] = totalProceeds / totalCost
          totalProceeds = totalCost = 0
      
      
      
      if(len(investorOfferID) < 12):
        print(trades["_links"]["operation"])
        print(investorOfferID)
      
      instructions = getMemoFromMakerOfferID(publicKey, investorOfferID)
      
#      if():
#        i am counter
#      else:
#        i am base
      
      
      # extract asset
      # part of averaged single sale? -> begin averaging
        # sum all bought / sum all given etc
      # extract value at txn for own benefit
      
      # a way to work cost basis into this ?
      
      
      # BASICALLY:
      # Can create account record for uncovered positions or pre-existing basis totally averaged out mst likely
      # When they go to sell, they pick the lot
      # Lots classified by OFFER_ID and averages as needed when providing liquidity
      # When selling (from account omnibus), Use MEMO "Disposing #{OFFER_ID}"
      
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  
    #- cycle through txns using taxYearStart to 
  
  pprint(b)
  
  return 0

# - figure out le tax
#   - sale proceeds 
#     - from purchase on Stellar
#     - from pre-existing cost basis
#       - incl. broker ACATS
# - pull pii record which has association for uncovered securities or pre-existing cost basis
# - sumbmit DIV to FIRE
# - export/email(?) 8949

# different doc:
#   - interest
#     - pay all dividends via USDC for recordkeeping?
# - export DIV


def getAllOfferIDsMappedToChiefMemosForAccount(publicKey):
  requestAddr = f"https://{HORIZON_INST}/accounts/{publicKey}/transactions?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for txns in blockchainRecords:
      if(txns["source_account"] != publicKey):
        continue
      resultXDR = TransactionResult.from_xdr(txns["result_xdr"])
      for ops in resultXDR.result.results:
        offerIDarr = []
        getOfferIDfromTxnOp(ops, offerIDarr)
        for offerIDs in offerIDarr:
          if(offerIDs and offerIDs not in allOfferIDsMappedToChiefMemosForAccount.keys()):
            try:
              memo = txns["memo"]
            except KeyError:
              memo = ""
            allOfferIDsMappedToChiefMemosForAccount[offerIDs] = memo
    # Go to next cursor
    requestAddr = data["_links"]["next"]["href"].replace("\u0026", "&")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  return 1

def getOfferIDfromTxnOp(op, offerIDarr):
  try:
    offerID = op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64
  except AttributeError:
    try:
      offerID = op.tr.manage_buy_offer_result.success.offer.offer.offer_id.int64
    except AttributeError:
      try:
        taker = len(op.tr.manage_sell_offer_result.success.offers_claimed)
        if(taker):
          for trades in op.tr.manage_sell_offer_result.success.offers_claimed:
            try:
              offerID = getOfferIDfromOmnibusContraOfferID(trades.order_book.offer_id.int64)
            except AttributeError:
              try:
                offerID = getOfferIDfromOmnibusContraOfferID(trades.liquidity_pool.offer_id.int64)
              except AttributeError:
                offerID = getOfferIDfromOmnibusContraOfferID(trades.v0.offer_id.int64)
            offerIDarr.append(offerID)
        else:
          offerID = getOfferIDfromOmnibusContraOfferID(op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64)
      except AttributeError:
        try:
          taker = len(op.tr.manage_buy_offer_result.success.offers_claimed)
          if(taker):
            for trades in op.tr.manage_buy_offer_result.success.offers_claimed:
              try:
                offerID = getOfferIDfromOmnibusContraOfferID(trades.order_book.offer_id.int64)
              except AttributeError:
                try:
                  offerID = getOfferIDfromOmnibusContraOfferID(trades.liquidity_pool.offer_id.int64)
                except AttributeError:
                  offerID = getOfferIDfromOmnibusContraOfferID(trades.v0.offer_id.int64)
              offerIDarr.append(offerID)
          else:
            offerID = getOfferIDfromOmnibusContraOfferID(op.tr.manage_sell_offer_result.success.offer.offer.offer_id.int64)
        except:
          return 0
  offerIDarr.append(offerID)
  return 1

def getOfferIDfromOmnibusContraOfferID(offerID):
  requestAddr = f"https://{HORIZON_INST}/offers/{offerID}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      try:
        if(trades["counter_account"] == publicKey):
          offerID = trades["counter_offer_id"]
        elif(trades["base_account"] == publicKey):
          offerID = trades["base_offer_id"]
      except KeyError:
        sys.exit(f"Error generating syntheic ID - check paging token")
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  return int(offerID)

def getBasisOrProceedsFromTrade():
  return 1

def getTradeProceedsFromOfferID(): # call if in tax year
  return 1

def getTradeQuantityAndBasisFromOfferID():
  return 1

def getTrades_Date_FromOfferID():
  totalFiatCost = totalFiatProceeds = totalSharesPurchased = totalSharesSold = Decimal("0")
  requestAddr = f"https://{HORIZON_INST}/offers/{offerIDs}/trades?limit={MAX_SEARCH}"
  data = requests.get(requestAddr).json()
  blockchainRecords = data["_embedded"]["records"]
  while(blockchainRecords != []):
    for trades in blockchainRecords:
      try:
        baseAsset = Asset(trades["base_asset_code"], trades["base_asset_issuer"])
      except KeyError:
        baseAsset = Asset.native()
      baseAssetFiat = baseAsset == USD_ASSET or baseAsset == USDC_ASSET
      try:
        counterAsset = Asset(trades["counter_asset_code"], trades["counter_asset_issuer"])
      except KeyError:
        counterAsset = Asset.native()
      counterAssetFiat = counterAsset == USD_ASSET or counterAsset == USDC_ASSET
      # Expect one asset to be fiat
      if(trades["base_account"] == publicKey):
        if(baseAssetFiat):
          totalFiatCost += Decimal(trades["base_amount"])
          totalSharesPurchased += Decimal(trades["counter_amount"])
        elif(counterAssetFiat):
          totalFiatProceeds += Decimal(trades["counter_amount"])
          totalSharesSold += Decimal(trades["base_amount"])
      elif(trades["counter_account"] == publicKey):
        if(counterAssetFiat):
          totalFiatCost += Decimal(trades["counter_amount"])
          totalSharesPurchased += Decimal(trades["base_amount"])
        elif(baseAssetFiat):
          totalFiatProceeds += Decimal(trades["base_amount"])
          totalSharesSold += Decimal(trades["counter_amount"])
    requestAddr = data["_links"]["next"]["href"].replace("%3A", ":")
    data = requests.get(requestAddr).json()
    blockchainRecords = data["_embedded"]["records"]
  if(totalSharesPurchased and totalSharesSold):
    sys.exit("Critical math error")
  return (totalFiatCost, totalFiatProceeds)




# step 1: get everything working
# step 2: deal with wash sales :)
# future features: support liquidity pool D/W
#                     (as interest income or cap gains? many aquisitions/dispositions?)
#                  path payments (incl. to self)

getAllOfferIDsMappedToChiefMemosForAccount(publicKey)
pprint(allOfferIDsMappedToChiefMemosForAccount)