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


if __name__ == "__main__":
  sample_code = get_contract("0x5c7AD3EB8264eF91dD4d756Ef9759F7aa86744e7")
  print(sample_code)