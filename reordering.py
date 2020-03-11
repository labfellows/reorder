# *** Reordering Script ***

# This script allows automatic reordering of inventory items when the available count drops below the specified floor and reorders to the specified ceiling. 

# Set up: 
# 1. Install requests module `pip install requests`
# 2. Create a min and max field and set the value on all inventory items that need to be automatically reordered. 
# 3. Specify the min and max field names within this script.
# 4. Insert authentication credentials.
# 5. Set up a cron job for this script or run manually as desired. 

# Known script limitations: 
# 1. Orders with groups that require approvals will still need to be approved in order for the order to go through.
# 2. If items reordered are not yet in inventory when the script runs again, the script will reorder these items again.
# 3. The first available group is auto-assigned to the order.
# 4. This script does not filter for pending orders. So rerunning before accepting items into inventory could result in duplicates.

import json
import base64
import requests

# TODO specify min and max field names (add these as field definitions to any inventory items you would like reordered)
MIN_FIELD = 'Minimum'
MAX_FIELD = 'Maximum'

# TODO insert credentials for authentication (see https://apidocs.labfellows.com for instructions)
BASE_URL = "https://api.labfellows.com/v2/"
API_KEY = "<YOUR_API_KEY_HERE>"
email = "<YOUR_EMAIL_HERE>"
subdomain = "<YOUR_SUBDOMAIN_HERE>"

encoded_auth = base64.encodebytes(('%s:%s' % (email, API_KEY)).encode('utf8')).decode('utf8').replace('\n', '')
headers = {
  'content-type': "application/vnd.api+json",
  'accept': "application/vnd.api+json",
  'x-authorization': "Bearer organization %s" % subdomain,
  'Authorization': "Basic %s" % encoded_auth
}

try:
  print('get field definitions and id of min and max fields...')
  inventory_definitions_url = BASE_URL + 'inventory_field_definitions'
  inventory_definitions_request = requests.get(inventory_definitions_url, headers=headers)
  inventory_definitions_request.raise_for_status()
  inventory_definitions = inventory_definitions_request.json()

  max_field_definition = [el for el in inventory_definitions['data'] if el['name'] == MAX_FIELD]
  max_field_definition_id = max_field_definition[0]['id'] if len(max_field_definition) > 0 else None
  if not max_field_definition_id:
    print('max field needs to be defined for reordering!')
    exit()

  min_field_definition = [el for el in inventory_definitions['data'] if el['name'] == MIN_FIELD]
  min_field_definition_id = min_field_definition[0]['id'] if len(min_field_definition) > 0 else None

  print('get inventory items with the max field name...')
  inventory_url = BASE_URL + 'inventory_items?inventory_field_definition_id=%s' % max_field_definition_id
  inventory_request = requests.get(inventory_url, headers=headers)
  inventory_request.raise_for_status()
  inventory_items = inventory_request.json()

  req_id = None

  reorder_items = []

  # loop over each inventory item
  for val in inventory_items['data']:
    available = val['available']

    max_obj = [el for el in val['field_values'] if el['definition_id'] == max_field_definition_id]
    max_val = int(max_obj[0]['value'])  # max value should always be present

    min_obj = [el for el in val['field_values'] if el['definition_id'] == min_field_definition_id]
    min_val = int(min_obj[0]['value']) if len(min_obj) > 0 else 0 # set min value to 0 if not set, but will be set to 0 if for some reason not present

    # Reorder items if available count drops below the minVal thresold or if the quantity available is 0)
    if min_val > available or available == 0:
      reorder_quantity = max_val - min_val
      item = val['name']
      print(f'reordering {item}: {reorder_quantity} units')
      reorder_items.append({
        'id': val['id'],
        'quantity_requested': max_val - min_val
      })

  if len(reorder_items) == 0:
    print('no items to reorder!')
    exit()

  print('submit items for reorder...')
  reorder_url = BASE_URL + 'inventory_items/reorder'
  reorder_request = requests.post(reorder_url, headers=headers, json={'items': reorder_items})
  reorder_request.raise_for_status()
  reorder_data = reorder_request.json()

  req_id = reorder_data['data'][0]['purchase_order']['requisition_id']
  print(f'requisition_id: {req_id}')

  print('get available groups...')
  groups_url =  BASE_URL + 'groups/my'
  groups_request = requests.get(groups_url, headers=headers)
  groups_request.raise_for_status()
  groups = groups_request.json()

  if len(groups['data']) > 0:
    print('assign first group to requisition if user has groups...')
    assign_group_url = BASE_URL + 'requisitions/%s' % req_id
    assign_group_request = requests.patch(assign_group_url, headers=headers, json={
      "group_id": groups['data'][0]['id']
    })
    assign_group_request.raise_for_status()
    assign_group_response = assign_group_request.json()
    # print(assign_group_response)

  print('submit requisition...')
  submit_url = BASE_URL + 'requisitions/%s/submit' % req_id
  submit_request = requests.post(submit_url, headers=headers)
  submit_request.raise_for_status()
  submit_response = submit_request.json()
  # print(submit_response)

  print('done!')

except requests.exceptions.RequestException as e:
  print(e)
  exit(1)
