import config
import requests

def get_contract(contract_address):

  api_endpoint = 'https://api.etherscan.io/api'
  params = {
    'module': 'contract',
    'action': 'getsourcecode',
    'address': contract_address,
    'apikey': config.etherscan_api_key
  }

  response = requests.get(api_endpoint, params=params)

  # Check if request was successful
  if response.status_code == 200:
    # Get Solidity source code from API response
    result = response.json()['result'][0]
    solidity_source_code = result['SourceCode']
    return solidity_source_code
  else:
    return f'Error: {response.status_code}'


def get_abi(address):
  # Replace with your own Etherscan API key
  api_key = config.etherscan_api_key
  
  # URL for the Etherscan API call to get the contract ABI
  url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={api_key}'
  
  # Make the API request and get the response
  response = requests.get(url)
  
  # If the request was successful, return the ABI as a string
  if response.status_code == 200:
    response_json = response.json()
    return response_json['result']
  
  # If the request was not successful, raise an exception
  else:
    raise Exception(f'Failed to get ABI at {address}')

if __name__ == "__main__":
  sample_code = get_contract("0xe24a08592213f59534f5cE77018Cb19B39094251")
  print(sample_code)
  # pair_address = '0xdCE928e379FF0fa3bDD6d7c1665949b9d528890E'
  # abi = get_uniswap_abi(pair_address)
  # print(abi)