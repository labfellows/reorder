# *** Reordering Script ***

# This script allows automatic reordering of inventory items when the available count drops below the specified minimum value and reorders to the specified maximum count. 

# Set up: 
# 1. Create a min and max field and set the value on all inventory items they would like automatically reordered. 
# 2. Specify the minimum and maximum field names within this script.
# 3. Insert authentication credentials.
# 4. Set up a cron job for this script or run manually as desired. 

# Known script limitations: 
# 1. Orders with groups that require approvals will still need to be approved in order for the order to go through
# 2. If items reordered are not yet in inventory when the script runs again, the script will reorder these items again
# 3. This script auto assigns the first available group to the order 

import json
import base64
import requests

# TODO specify minimum and maximum field names (add these as field definitions to any inventory items you would like reordered)
minimum = 'Minimum'
maximum = 'Maximum'

# TODO insert credentials for authentication (see https://apidocs.labfellows.com for instructions)
email = "test@test.com"
api_key = "12345"
subdomain = "labfellows"
base_url = "https://api.labfellows.com/"

encoded_auth = base64.encodebytes(('%s:%s' % (email, api_key)).encode('utf8')).decode('utf8').replace('\n', '')

headers = {
    'content-type': "application/vnd.api+json",
    'accept': "application/vnd.api+json",
    'x-authorization': "Bearer organization %s" % subdomain,
    'Authorization': "Basic %s" % encoded_auth
    }

# get field definitions and find id of maximum and minimum

inventory_definitions_url = base_url + 'v2/inventory_field_definitions'

inventory_definitions_request = requests.get(inventory_definitions_url, headers=headers)
inventory_definitions = inventory_definitions_request.json()

max_field_definition = [el for el in inventory_definitions['data'] if el['name'] == maximum]
min_field_definition = [el for el in inventory_definitions['data'] if el['name'] == minimum]

max_field_definition_id = max_field_definition[0]['id'] if len(max_field_definition) > 0 else None
min_field_definition_id = min_field_definition[0]['id'] if len(min_field_definition) > 0 else None

# get inventory items with the maximum field name 
inventory_url = base_url + 'v2/inventory_items?inventory_field_definition_id=%s' % max_field_definition_id

inventory_request = requests.get(inventory_url, headers=headers)
inventory_items = inventory_request.json()

req_id = None

# loop over each inventory item
for val in inventory_items['data']:
  available = val['available']

  min_obj = [el for el in val['field_values'] if el['definition_id'] == min_field_definition_id]
  max_obj = [el for el in val['field_values'] if el['definition_id'] == max_field_definition_id]

  min_val = int(min_obj[0]['value']) if len(min_obj) > 0 else 0 # set min value to 0 if not set
  max_val = int(max_obj[0]['value']) if len(max_obj) > 0 else 0 # max value should always be present, but will be set to 0 if for some reason not present

  # Reorder items if available count drops below the minVal thresold or if the quantity available is 0
  if min_val > available or available == 0:
    payload = {
        "lines": [
          {
            "catalog_item_id": val['catalog_item']['id'],
            "quantity_requested": max_val - min_val,
            "unit_of_measure": val['unit_of_measure'],
            "price_in_cents": val['price_in_cents']
          }
        ]
    }

    reorder_url = base_url + 'v2/purchase_order_lines/reorder'
    reorder_request = requests.post(reorder_url, headers=headers, json=payload)
    reorder_data = reorder_request.json()

    req_id = reorder_data['data'][0]['purchase_order']['requisition_id']

    print(req_id)

if req_id:
  # Get available groups 
  groups_url =  base_url + 'v2/groups/my'
  groups_request = requests.get(groups_url, headers=headers)
  groups = groups_request.json()

  # assign first group to requisition if user has groups
  if len(groups['data']) > 0:
    assign_group_url = base_url + 'v2/requisitions/%s' % req_id

    group_payload = {
      "group_id": groups['data'][0]['id']
    }
    assign_group_request = requests.patch(assign_group_url, headers=headers, json=group_payload)
    assign_group_response = assign_group_request.json()
    print(assign_group_response)

  # submit requisition
  submit_url = base_url + 'v2/requisitions/%s/submit' % req_id

  submit_request = requests.post(submit_url, headers=headers)
  submit_response = submit_request.json()
  print(submit_response)