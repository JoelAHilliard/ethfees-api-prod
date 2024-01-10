import requests
from settings import *
from flask import json
# from web3 import Web3
import pandas as pd
# w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/cc8dc3c93199436990f537324d8779d8"))

import time
def weiToEth(wei):
    return wei / 1000000000000000000


def heatmap_of_activity(data):
    df = pd.DataFrame(data)
    default_timestamp = 0  # You can set this to an appropriate default value
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    
    # Drop any rows with NaN in the timestamp column (after conversion to numeric)
    df = df.dropna(subset=['timestamp'])

    # Convert to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')

    df['day_of_week'] = df['timestamp'].dt.dayofweek  # Returns the day index (0 = Monday, 6 = Sunday)
    df['hour'] = df['timestamp'].dt.hour
    heatmap_data = df.pivot_table(index='day_of_week', columns='hour', values='hash', aggfunc='count', fill_value=0)
    result = [[day_index, hour_index, count] for day_index, row in heatmap_data.iterrows() for hour_index, count in row.items()]

    return result


def transaction_volume_distribution(data):
    df = pd.DataFrame(data)
    bins = [0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 1]
    labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
    df['gas_spent_bin'] = pd.cut(df['gas_spent'], bins=bins, labels=labels)
    result = [{"range": label, "count": count} for label, count in df['gas_spent_bin'].value_counts().items()]
    return result


def daily_transaction_count_trend(data):
    df = pd.DataFrame(data)
    default_timestamp = 0  # You can set this to an appropriate default value
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    
    # Drop any rows with NaN in the timestamp column (after conversion to numeric)
    df = df.dropna(subset=['timestamp'])

    # Convert to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')

    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour
    daily_transaction_count = df.resample('D', on='timestamp')['hash'].count()
    result = [{"date": str(date), "count": count} for date, count in daily_transaction_count.items()]
    return result

def gas_spent_vs_time_of_day(data):
    df = pd.DataFrame(data)
    default_timestamp = 0  # You can set this to an appropriate default value
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    
    # Drop any rows with NaN in the timestamp column (after conversion to numeric)
    df = df.dropna(subset=['timestamp'])

    # Convert to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')

    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour
    result = [{"hour": hour, "gas_spent": gas_spent} for hour, gas_spent in zip(df['hour'], df['gas_spent'])]
    return result



def top_receiving_addresses(data):
    df = pd.DataFrame(data)
    top_receivers = df['to'].value_counts().nlargest(10)
    result = [{"address": address, "count": count} for address, count in top_receivers.items()]
    return result

def transaction_network_map(data):
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(data)
    
    # Group by 'from' and 'to' addresses and count the occurrences
    connections = df.groupby(['from', 'to']).size().reset_index(name='count')
    
    # Extract unique nodes and edges
    nodes = list(set(connections['from']).union(set(connections['to'])))
    edges = [{"from": row['from'], "to": row['to'], "count": row['count']} for _, row in connections.iterrows()]
    
    result = {"nodes": nodes, "edges": edges}
    return result

def getEthPrice():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
    try:
        res = requests.get(url)
        json_res = json.loads(res.text)
        return json_res['ethereum']['usd']
    except:
        return {
            'error': "Error"
        }
        
def getGasPrices():
    url = 'https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=' + ETHER_SCAN_API_KEY

    try:
        res = requests.get(url)
        json_res = json.loads(res.text)
        data = {
            'fastGas': json_res['result']['FastGasPrice'],
            'proposedGas': json_res['result']['ProposeGasPrice'],
            'safeGas': json_res['result']['SafeGasPrice']
        }
    except:
        data = {
            'error': "Please try again."
        }
    return data

def checkWallet(wallet):
    if(wallet[0] != '0' and wallet[1] != 'x'):
        return False
    return True
def getBalance(wallet):
    try:
        response = w3.eth.getBalance(wallet)
        balance = response / 1000000000000000000
        return balance
    except:
        pass
    try:
        url = "https://api.etherscan.io/api?module=account&action=balance&address="+wallet+"&tag=latest&apikey=" + ETHER_SCAN_API_KEY
        res = requests.get(url)
        json_res = json.loads(res.text)
        return int(json_res["result"]) / 1000000000000000000
    except:
        return -1


def getTxs(wallet):

    url = "https://api.etherscan.io/api?module=account&action=txlist&address=" + wallet +"&startblock=0" + "&endblock=latest&page=1&offset=5000&sort=asc&apikey=" + ETHER_SCAN_API_KEY
    res = requests.get(url)
    json_res = res.json()





    total_tx = 0
    total_failed_tx = 0 
    total_eth_spent = 0
    total_eth_failed = 0
    total_gwei = 0

    txs=[]

    for tx in json_res['result']:
        total_eth_spent = 0

        if(tx['from'].upper() == wallet.upper() and not int(tx['isError'])):

            total_tx+=1
            total_eth_spent += (float(tx['gasPrice']) * float(tx['gasUsed'])) / 1000000000000000000
            txs.append({
                "hash":tx['hash'],
                "from":tx['from'],
                "to":tx['to'],
                "gas_spent":total_eth_spent,
                "failed":"false",
                "timestamp":tx['timeStamp']
            })
            total_gwei += (float(tx['gasPrice']) * 0.000000001)
        
        if(int(tx['isError'])):
            total_eth_failed += float(tx['gasPrice']) * float(tx['gasUsed']) / 1000000000000000000

            total_failed_tx += 1

            txs.append({
                "hash":tx['hash'],
                "from":tx['from'],
                "to":tx['to'],
                "gas_spent":total_eth_spent,
                "failed":"true"
            
            })
            


    return {
        "txs":txs,
        "transaction_network":transaction_network_map(txs),
        "transaction_volume_dist":transaction_volume_distribution(txs),
        "heatmap":heatmap_of_activity(txs),
        "top_receiving":top_receiving_addresses(txs),
        "daily_tx_count_trend":daily_transaction_count_trend(txs),
        "gas_spent_vs_time_of_day":gas_spent_vs_time_of_day(txs)
    }

def getGasInfo(wallet):
    # return total tx, failed tx, total eth spent, total eth failed, avg gwei in dictionary form
    # collection = db['Wallets']['gasInfo']

    #start block is inclusive, not sure about end block


    result = None
    url = "https://api.etherscan.io/api?module=account&action=txlist&address=" + wallet +"&startblock=0" + "&endblock=latest&page=1&offset=5000&sort=asc&apikey=" + ETHER_SCAN_API_KEY



    total_tx = 0
    total_failed_tx = 0 
    total_eth_spent = 0
    total_eth_failed = 0
    total_gwei = 0
   
    res = requests.get(url)
    json_res = res.json()

    avgGwei = 0

    for tx in json_res['result']:
        if(tx['from'].upper() == wallet.upper() and not int(tx['isError'])):
            total_tx+=1
            total_eth_spent += (float(tx['gasPrice']) * float(tx['gasUsed'])) / 1000000000000000000
            total_gwei += (float(tx['gasPrice']) * 0.000000001)
        
        if(int(tx['isError'])):
            total_eth_failed += float(tx['gasPrice']) * float(tx['gasUsed']) / 1000000000000000000
            total_failed_tx += 1
    
    result = {
        'walletAddress': wallet,
        'total_tx': total_tx,
        'total_failed_tx': total_failed_tx,
        'total_eth_spent': total_eth_spent,
        'total_eth_failed': total_eth_failed,
        'total_gwei': total_gwei
    }
    try: 
        avgGwei = total_gwei / total_tx
    except: 
        avgGwei = 0

    data = {
        "successfulTxs": total_tx-total_failed_tx ,
        "ethSpentSuccessful": total_eth_spent,
        "failedTxs": total_failed_tx,
        "ethSpentFailed": total_eth_failed,
        "avgGwei": avgGwei
    }
    return data

def testAgainstDB(contractObjects):

    #return an array of contract info (includes new additions)

    collection = db['rest']['test2']
    matchingItems = []
    for contract in contractObjects:
        result = (collection.find_one({'collectionAddress': contract['address']}))
        if(result is None):
            result = {
                'collectionAddress': contract['address'],
                'floor_price': -1,
                'slug': contract['slug']
            }
            collection.insert_one(result)
        result.pop('_id')
        result['owned_asset_count'] = contract['owned_asset_count']
        matchingItems.append(result)
    return matchingItems

def getERC20Tokens(wallet):
    url = "https://api.bloxy.info/address/balance?address=" + wallet + "&chain=eth&key=ACCB3x70GOFD6&format=structure"

    r = requests.get(url)
    content = r.json()
    someBalance = []

    for token in content:
        if(token["token_type"] == "ERC20" and token["balance"] > 0.000001 and token["symbol"] != "UD"):
            someBalance.append(
                {
                    "symbol": token["symbol"],
                    "token_address": token["token_address"],

                    "sent_amount": token["sent_amount"],
                    "received_amount": token["received_amount"],

                    "balance": token["balance"]
                }
            )
    
    return someBalance

def get721Tokens(wallet):
    headers = {
        "Accept": "application/json",
        "X-API-KEY": "8426734538df46b3b7584aaf39284614"
    }
    #takes in wallet address
    # returns list of dictionaries of Contract Addresses and slugs
    url = "https://api.opensea.io/api/v1/collections?asset_owner=" + wallet

    try:
        r = requests.get(url, headers=headers)
        print(r)
        content = r.json()
        contracts = []
        contractIDS = []
    except:
        print("failed")
        return


    for contract in content:
        contracts.append({'contract':contract['primary_asset_contracts'], 'slug': contract['slug'], 'owned_asset_count': contract['owned_asset_count']})

    for contract in contracts:
        try:
            contractIDS.append({'address': contract['contract'][0]['address'], 'slug': contract['slug'], 'owned_asset_count': contract['owned_asset_count']})
        except:
            print("Some error")
    return contractIDS





def measureTime(function):
    wallet = "0x1Ac1Edb70367f3e9C0602dcEd488a465565F256E"
    start_time = time.time()
    function(wallet)
    end_time = time.time()
    print(end_time - start_time)
#get721Tokens('0x1Ac1Edb70367f3e9C0602dcEd488a465565F256E')
# gasTotal = 0

# wallet = '0x1Ac1Edb70367f3e9C0602dcEd488a465565F256E'
# print("Data for " + wallet)
# data = getGasInfo(wallet)
# print(data)
# print()

# gasTotal += float(data['ethSpentSuccessful'])
# gasTotal += float(data['ethSpentFailed'])

# wallet2 = '0xD9D40B363501AF8a71995E265455957e0BA68B9C'
# print("Data for " + wallet2)
# data = getGasInfo(wallet2)
# print(data)
# print()

# gasTotal += float(data['ethSpentSuccessful'])
# gasTotal += float(data['ethSpentFailed'])

# wallet3 = '0xCe3230efCEdcb5984efd3F3b1E63cF08a5325E44'
# print("Data for " + wallet3)
# data = getGasInfo(wallet3)
# print(data)
# print()

# gasTotal += float(data['ethSpentSuccessful'])
# gasTotal += float(data['ethSpentFailed'])

# wallet4 = '0x75aFC1362262E9a0bF70846DF88336951ef06D7F'
# print("Data for " + wallet4)
# data = getGasInfo(wallet4)
# print(data)
# print()

# gasTotal += float(data['ethSpentSuccessful'])
# gasTotal += float(data['ethSpentFailed'])


# print("Total ETH spent on gas: " + str(gasTotal))
# print()

# print(measureTime(getGasInfo))