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
url = "https://ssapi.shipstation.com/orders?orderDateStart=2021-08-14"
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
TwoPacksSold = 0


for order in data['orders']:
    skuValue = order['items'][0]['sku']
    sku = 0
    # Handles RED/02 (M1010-2) 
    if '(' in skuValue:
        sku = skuValue.split('(')[1]
        sku = sku.split('-')[1]
        sku = sku.split(')')[0]
        sku = int(sku)

    # Handles RED/02+CFA10
    elif '+' in skuValue and '/' in skuValue:
        sku = 2
    
    # Handles M1030-02/BLK
    elif  '/' in skuValue:
        sku = skuValue.split('-')[1]
        sku = sku.split('/')[0]
        sku = int(sku)

    # Handles M1000
    elif '-' not in skuValue:
        sku = 0
    else:
        sku = int(skuValue.split('-')[1])
    # Dividing the sky after the - for 2, 4, 6, 10 packs by 2 then multiplying by quantity to get total amount of 2 packs sold. 
    quantity = int(order['items'][0]['quantity'])
    if sku > 1 : 
        TwoPacksSold = (sku / 2) * quantity
    else :
        TwoPacksSold = sku * quantity
    row = {
        'orderId': order['orderId'],
        'orderDate' : order['orderDate'],
        'orderStatus' : order['orderStatus'],
        'name' : order['items'][0]['name'],
        'sku' : skuValue,
        'quantity' : order['items'][0]['quantity'],
        'amountPaid' :  order['amountPaid'],
        'TwoPacksSold' : TwoPacksSold,
        'totalAmountPaid' : '',
        'total2PacksSold' : ''
    }
    total2PacksSold += TwoPacksSold
    totalAmountPaid +=  row['amountPaid']
    results.append(row)
    
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




BLK02 = df.loc[df['sku'].str.contains('M1030') | df['sku'].str.contains('BLK')]
sumBLK = BLK02['TwoPacksSold'].sum()
GRY02 = df.loc[df['sku'].str.contains('M1040') | df['sku'].str.contains('GRY')]
sumGRY = GRY02['TwoPacksSold'].sum()
PNK02 = df.loc[df['sku'].str.contains('M1070') | df['sku'].str.contains('PNK')]
sumPNK = PNK02['TwoPacksSold'].sum()
RED02 = df.loc[df['sku'].str.contains('M1010') | df['sku'].str.contains('RED')]
sumRED = RED02['TwoPacksSold'].sum()
ROS02 = df.loc[df['sku'].str.contains('M1080') | df['sku'].str.contains('ROS')]
sumROS = ROS02['TwoPacksSold'].sum()

colorsSold = {
        'BLK/02 Sold' : sumBLK,
        'GRY/02 Sold' : sumGRY,
        'PNK/02 Sold' : sumPNK,
        'RED/02 Sold' : sumRED,
        'ROS/02 Sold' : sumROS,
        'Total Two Packs Sold': total2PacksSold,
        'Total Amount Paid': totalAmountPaid
}
finalResults = [colorsSold]

df2 = pd.DataFrame(finalResults)


curr_date = datetime.today()
curr_date = curr_date.strftime('%m_%d_%y')
df2.to_csv('{}_Final_Inventory_as_of_AUG14.csv'.format(curr_date))