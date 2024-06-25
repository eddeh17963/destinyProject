import requests
import json

BASE_URL = "https://www.bungie.net/Platform/Destiny2/"#Manifest/DestinyInventoryItemDefinition/4017959782/"

payload = {}
headers = {
  'X-API-Key': 'ecc0e5e526e44bbbb89b0e77dc399a1c'
  }

def get_item_info(id):
  return requests.get(BASE_URL + f"Manifest/DestinyInventoryItemDefinition/{str(id)}/", headers=headers, data=payload)

ex = 4017959782
print(json.dumps(get_item_info(ex).json(), indent=3))

