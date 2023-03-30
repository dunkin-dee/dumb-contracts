import requests
from datetime import datetime, timedelta


def get_weth_volume(address, start_time):
  # Set the Uniswap subgraph URL
  uniswap_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

  # Set the Uniswap pool address and time
  start_timestamp = int((datetime.fromtimestamp(start_time).replace(minute=0, second=0) - timedelta(seconds=30)).timestamp())
  pair_address = address.lower()

  # Set the GraphQL query
  query = '''
    query {
    pairHourDatas(
        where: {
          pair: "%s"
          hourStartUnix_gt: %i
        }, 
        orderBy: hourStartUnix, 
        orderDirection: asc,
        first: 24) {
      hourlyVolumeToken0
      hourlyVolumeToken1
    }
  }
  '''%(pair_address, start_timestamp)

  # Send the GraphQL request
  response = requests.post(uniswap_url, json={'query': query})

  # Parse the response JSON
  data = response.json()
  token0 = 0
  token1 = 0
  for hour_data in data['data']['pairHourDatas']:
    token0 += float(hour_data['hourlyVolumeToken0'])
    token1 += float(hour_data['hourlyVolumeToken1'])

  return min([token0, token1])


def get_trade_start(address, start_time):
  # Set the Uniswap subgraph URL
  uniswap_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

  # Set the Uniswap pool address and time
  start_timestamp = int((datetime.fromtimestamp(start_time).replace(minute=0, second=0) - timedelta(seconds=30)).timestamp())
  pair_address = address.lower()

  # Set the GraphQL query
  query = '''
    query {
    pairHourDatas(
        where: {
          pair: "%s"
          hourStartUnix_gt: %i
        }, 
        orderBy: hourStartUnix, 
        orderDirection: asc,
        first: 24) {
      hourStartUnix
      hourlyVolumeToken0
      hourlyVolumeToken1
    }
  }
  '''%(pair_address, start_timestamp)

  # Send the GraphQL request
  response = requests.post(uniswap_url, json={'query': query})

  # Parse the response JSON
  data = response.json()

  for hour_data in data['data']['pairHourDatas']:
    if float(hour_data['hourlyVolumeToken0']) > 0:
      return int(hour_data['hourStartUnix'])
    
  


if __name__ == "__main__":
  h = get_trade_start("0xA9Cac16fE9f7CEABfDd0D99A8168A27D23037D52".lower(), int((datetime.now() - timedelta(days=9)).timestamp()))
  v = get_weth_volume("0xA9Cac16fE9f7CEABfDd0D99A8168A27D23037D52".lower(), h)
  print(v)
