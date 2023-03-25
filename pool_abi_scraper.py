import requests
import config

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
  pair_address = '0x2B296315e940B0382B2Ec0620399Ec239fFe6CfB'
  abi = get_uniswap_pair_abi(pair_address)
  print(abi)
