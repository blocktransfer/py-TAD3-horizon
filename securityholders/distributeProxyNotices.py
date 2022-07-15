import sys
sys.path.append("../")
from globals import *
from stellar_sdk import exceptions

try:
  SECRET = sys.argv[1]
except Exception:
  print("Running without mailing auth")

try:
  SECRET = sys.argv[1]
except Exception:
  print("Running without email auth")

def distributeProxyNotices(queryAsset):
  # fetch record date (queryAsset) using Open, .read().strip().split("\n") , Split; return ...
  for shareholders in recordDateList:
    email = lines[6]
    if(email):
      emailProxyNotice(shareholders)
      # time.sleep(20) ?
    else:
      mailProxyNotice(shareholders)
  # make virtual proxy notice onchain? 

