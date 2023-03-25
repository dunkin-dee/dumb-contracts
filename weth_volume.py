import requests
from datetime import datetime, timedelta


def get_weth_volume(address, start_time):
  # Set the Uniswap subgraph URL
  uniswap_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

  # Set the Uniswap pool address and time
  start_timestamp = int((datetime.fromtimestamp(start_time).replace(minute=0, second=0) - timedelta(seconds=30)).timestamp())
  end_timestamp = int((datetime.fromtimestamp(start_timestamp) + timedelta(hours=24)).timestamp())
  pair_address = address.lower()

  # Set the GraphQL query
  query = '''
    query {
    pairHourDatas(
        where: {
          pair: "%s"
          hourStartUnix_gt: %i
          hourStartUnix_lt: %i
        }, 
        orderBy: hourStartUnix, 
        orderDirection: desc,
        first: 24) {
      hourlyVolumeToken0
      hourlyVolumeToken1
    }
  }
  '''%(pair_address, start_timestamp, end_timestamp)

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


if __name__ == "__main__":
  h = get_weth_volume("0x2B296315e940B0382B2Ec0620399Ec239fFe6CfB", int((datetime.now() - timedelta(hours=28)).timestamp()))
  print(h)
