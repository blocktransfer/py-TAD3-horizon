import sys
sys.path.append("../")
from globals import *

def personaCallback():
  url = "https://withpersona.com/api/v1/inquiries?filter[account-id]=act_QDWvTTjRmuSSXdmVdz1srsxU"
  url = "https://withpersona.com/api/v1/accounts/act_QDWvTTjRmuSSXdmVdz1srsxU"

  headers = {
    "Authorization": f"Bearer {PERSONA_API_KEY}",
    "Persona-Version": "2023-01-05"
  }
  response = requests.get(url, headers = headers)
  
  print(response.json())

personaCallback()

"""
'address': {'type': 'hash', 'value': {
  'city': {'type': 'string', 'value': 'Atlanta'},
  'country_code': {'type': 'string', 'value': 'US'},
  'postal_code': {'type': 'string', 'value': '303050000'},
  'street_1': {'type': 'string', 'value': '2500 Peachtree Rd Nw Apt #1000'},
  'street_2': {'type': 'string', 'value': None},
  'subdivision': {'type': 'string', 'value': 'Georgia'}
}},
"""