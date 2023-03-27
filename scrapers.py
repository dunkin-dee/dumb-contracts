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


def get_uniswap_pair_abi(pair_address):
  # Replace with your own Etherscan API key
  api_key = config.etherscan_api_key
  
  # URL for the Etherscan API call to get the contract ABI
  url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={pair_address}&apikey={api_key}'
  
  # Make the API request and get the response
  response = requests.get(url)
  
  # If the request was successful, return the ABI as a string
  if response.status_code == 200:
    response_json = response.json()
    return response_json['result']
  
  # If the request was not successful, raise an exception
  else:
    raise Exception(f'Failed to get ABI for Uniswap pair at address {pair_address}')

if __name__ == "__main__":
  # sample_code = get_contract("0x5c7AD3EB8264eF91dD4d756Ef9759F7aa86744e7")
  # print(sample_code)
  pair_address = '0x2B296315e940B0382B2Ec0620399Ec239fFe6CfB'
  abi = get_uniswap_pair_abi(pair_address)
  print(abi)