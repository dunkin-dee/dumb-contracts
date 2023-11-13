import requests
import json
import config
from web3 import Web3
from uniswap import Uniswap
from pprint import pprint


w3 = Web3(Web3.HTTPProvider(config.infura_address))


def get_hourly_pool_reserves(pool_address):
    # Define the GraphQL query
    query = """
    query {
    pairHourDatas(
        where: {
          pair: "%s"
        }, 
        orderBy: hourStartUnix, 
        orderDirection: asc,
        first: 20) {
      hourStartUnix
      reserve0
      reserve1
      pair {
          token0{
            id
          }
        }
    }
  }
  """ % (
        pool_address
    )

    # Send the GraphQL request to Uniswap API endpoint
    response = requests.post(
        "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
        json={"query": query},
    )

    # Check if the request was successful
    if response.status_code == 200:
        prices = []
        # Parse the JSON response
        json_data = json.loads(response.text)
        pair_hour_data = json_data["data"]["pairHourDatas"]
        if (
            pair_hour_data[0]["pair"]["token0"]["id"]
            == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        ):
            weth_key = "reserve0"
            token_key = "reserve1"
        else:
            weth_key = "reserve1"
            token_key = "reserve0"

        for hour_details in pair_hour_data:
            prices.append(
                {
                    "timestamp": hour_details["hourStartUnix"],
                    "price": float(hour_details[weth_key])
                    / float(hour_details[token_key]),
                }
            )
        return prices
    else:
        # Handle any errors
        raise Exception(
            "Error retrieving Uniswap pool OHLC data. Status code: "
            + str(response.status_code)
        )


def get_addliquidity_hash(pair_address):
    # Set up the API endpoint
    api_endpoint = "https://api.etherscan.io/api"
    # Set up the API parameters for the event logs
    params = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": "0",
        "toBlock": "latest",
        "address": pair_address,
        "page": 1,
        "offset": 1,
        "sort": "asc",
        "apikey": config.etherscan_api_key,
    }
    # Send the API request and retrieve the response
    response = requests.get(api_endpoint, params=params).json()
    add_liquidity_event = response["result"][0]
    tx_hash = add_liquidity_event["transactionHash"]
    timestamp = int(add_liquidity_event["timeStamp"], 16)
    return timestamp, tx_hash


def get_addliquidity_decoded(transaction_hash):
    # Connect to Ethereum network
    w3 = Web3(Web3.HTTPProvider(config.infura_address))
    # Connect to Uniswap v2
    uniswap = Uniswap(
        address=None, private_key=None, version=2, provider=config.infura_address
    )
    # Get transaction receipt
    input_data = w3.eth.getTransaction(transaction_hash).input
    method_id = input_data[:10]
    if method_id == "0x0ed23b59":  # addLiquidity method id
        decoded_data = {
            "method": "addLiquidity",
            "tokenA": "0x" + input_data[34:74],
            "tokenB": "0x" + input_data[108:138],
            "amountADesired": int(input_data[138:202], 16),
            "amountBDesired": int(input_data[202:266], 16),
            "amountAMin": int(input_data[266:330], 16),
            "amountBMin": int(input_data[330:394], 16),
            "to": "0x" + input_data[394:454],
            "deadline": int(input_data[454:514], 16),
        }
        return decoded_data
    elif method_id == "0xf305d719":  # addLiquidityETH method id
        decoded_data = {
            "method": "addLiquidityETH",
            "token": "0x" + input_data[34:74],
            "amountTokenDesired": int(input_data[74:138], 16),
            "amountTokenMin": int(input_data[138:202], 16),
            "amountETHMin": int(input_data[202:266], 16),
            "to": "0x" + input_data[266:330],
            "deadline": int(input_data[330:], 16),
        }
        return decoded_data
    else:
        logs = w3.eth.getTransactionReceipt(transaction_hash).logs
        minted_amounts = logs[-2].data
        amount_token_a, amount_token_b = (
            int(minted_amounts[:66], 16),
            int(minted_amounts[66:], 16),
        )
        token_a = "0x" + logs[1].topics[1].hex()[26:]
        token_b = "0x" + logs[1].topics[2].hex()[26:]

        decoded_data = {
            "method": "openTrading",
            "amountA": amount_token_a,
            "amountB": amount_token_b,
            "tokenA": token_a,
            "tokenB": token_b,
        }
        return decoded_data


def get_token_and_eth_added(decoded_data):
    # Define the contract ABI
    contract_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        }
    ]
    # Create a contract instance
    if decoded_data["method"] == "addLiquidity":
        if (
            decoded_data["tokenA"].lower()
            == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        ):
            token_contract_address = decoded_data["tokenB"]
            token_amount = decoded_data["amountBDesired"]
            eth_amount = decoded_data["amountAMin"]
        else:
            token_contract_address = decoded_data["tokenA"]
            token_amount = decoded_data["amountADesired"]
            eth_amount = decoded_data["amountBMin"]

    elif decoded_data["method"] == "addLiquidityETH":
        token_contract_address = decoded_data["token"]
        token_amount = decoded_data["amountTokenDesired"]
        eth_amount = decoded_data["amountETHMin"]

    elif decoded_data["method"] == "openTrading":
        if (
            decoded_data["tokenA"].lower()
            == "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        ):
            token_contract_address = decoded_data["tokenB"]
            token_amount = decoded_data["amountB"]
            eth_amount = decoded_data["amountA"]
        else:
            token_contract_address = decoded_data["tokenA"]
            token_amount = decoded_data["amountA"]
            eth_amount = decoded_data["amountB"]

    contract = w3.eth.contract(
        address=w3.toChecksumAddress(token_contract_address),
        abi=contract_abi,
    )
    # Call the decimals function to get the number of decimals used by the token
    decimals = contract.functions.decimals().call()
    token_amount = token_amount / (10**decimals)
    eth_amount = eth_amount / (10**18)
    return decimals, token_amount, eth_amount


if __name__ == "__main__":
    pa = "0xdfCdDd91B38da683864480e683021387ec3E7048"

    # prices = get_hourly_pool_reserves(pa)
    # print(prices)
    ts, tx_hash = get_addliquidity_hash(pa)
    token_data = get_addliquidity_decoded(tx_hash)
    decimals, token_amount, eth_amount = get_token_and_eth_added(token_data)
    print(decimals, token_amount, eth_amount)
