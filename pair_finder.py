import requests
import config

import requests

def get_uniswap_pairs(from_block, to_block, api_key):
  # Set the Uniswap factory contract address
  factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
  
  # Set the API endpoint URL and parameters for retrieving the factory's PairCreated events
  endpoint = "https://api.etherscan.io/api"
  params = {
    "module": "logs",
    "action": "getLogs",
    "fromBlock": from_block,
    "toBlock": to_block,
    "address": factory_address,
    "topic0": "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9",
    "apikey": api_key
  }
  
  # Send the API request and parse the response
  response = requests.get(endpoint, params=params)
  if response.status_code != 200:
    raise Exception(f"Etherscan API returned status code {response.status_code}")
  response_data = response.json()
  if response_data["status"] != "1":
    raise Exception(f"Etherscan API returned error message: {response_data['message']}")
  
  # Extract the pair data from the response
  pairs = []
  for log in response_data["result"]:
    pair = {}
    pair["token0"] = "0x"+log["topics"][1][-40:]
    pair["token1"] = "0x"+log["topics"][2][-40:]
    pair["pair_address"] = log["address"]
    pair["block_number"] = int(log["blockNumber"], 0)
    pair["timestamp"] = int(log["timeStamp"], 0)
    pairs.append(pair)
  return pairs


if __name__ == "__main__":
  events = get_uniswap_pairs(16910501, 16910568, config.etherscan_api_key)
  print(events)

