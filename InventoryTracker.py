# Module Imports
from types import DynamicClassAttribute
import requests as req
import pandas as pd
from datetime import datetime
import json


#Grabs AUTH from credentials file as to keep encrypted.
AUTH_KEY = ''
AUTH_SECRET = ''
AUTH_ENCODED = ''
with open('credentials.txt','r') as f:
        for line in f:
            if 'key' in line: 
                AUTH_KEY = line.split('=')[1]
            if 'secret' in line:
                AUTH_SECRET = line.split('=')[1]
            if 'encoded' in line:
                AUTH_ENCODED = line.split('=')[1] + "="

# Endpoint URL
url = "https://ssapi.shipstation.com/orders?orderDateStart=2021-07-14"
headers = {
    "Authorization": "Basic " + AUTH_ENCODED
}
# send GET request to Endpoint with headers
response = req.get(url, headers=headers)

# print(response.json())
# output JSON file
with open ('data.json','w+') as f:
     json.dump(response.json(),f, indent=4)

#loads response json into a dictionary
data = response.json()

results = []

total2PacksSold = 0
totalAmountPaid = 0

for order in data['orders']:
    
    sku = order['items'][0]['sku']
    # Changed this to account for skew codes without - 
    if sku.find('-') == 1 : 
        sku = sku.split('-')[1]
    else : 
        sku = sku

    sku = sku.split('/')[0]
    #if  sku.is_integer() :
       
    sku = int(float(sku))
    TwoPacksSold = 0
    quantity = int(order['items'][0]['quantity'])
    # Dividing the sky after the - for 2, 4, 6, 10 packs by 2 then multiplying by quantity to get total amount of 2 packs sold. 
    if sku > 1 : 
        TwoPacksSold = (sku / 2) * quantity
    else :
        TwoPacksSold = sku * quantity
    row = {
        'orderId': order['orderId'],
        'orderDate' : order['orderDate'],
        'orderStatus' : order['orderStatus'],
        'name' : order['items'][0]['name'],
        'sku' : order['items'][0]['sku'],
        'quantity' : order['items'][0]['quantity'],
        'amountPaid' : order['amountPaid'],
        'TwoPacksSold' : TwoPacksSold,
        'totalAmountPaid' : '',
        'total2PacksSold' : ''
    }
    total2PacksSold += TwoPacksSold
    totalAmountPaid += row['amountPaid']
    results.append(row)
    print(sku)
    
row = {
        'orderId': '',
        'orderDate' : '',
        'orderStatus' : '',
        'name' : '',
        'sku' : '',
        'quantity' : '',
        'amountPaid' : '',
        'TwoPacksSold' : '',
        'totalAmountPaid' : totalAmountPaid,
        'total2PacksSold' : total2PacksSold
    }
results.append(row)    
df = pd.DataFrame(results)
df = df.reset_index(drop=True)

curr_date = datetime.today()
curr_date = curr_date.strftime('%m_%d_%y')
df.to_csv('{}_Updated_Inventory.csv'.format(curr_date))