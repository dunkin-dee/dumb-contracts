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
        first: 1) {
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
    
def get_pool_weth(address, start_time):
  # Set the Uniswap subgraph URL
  uniswap_url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

  # Set the Uniswap pool address
  pair_address = address.lower()

  # Set the GraphQL query
  query = '''
    query {
      pairDayDatas(
        where: {
          pairAddress: "%s",
          date_lt: %i
          },
          first: 1, 
          orderBy: date, 
          orderDirection: desc) {
        date
        reserve0
        reserve1
        token0 {
          id
        }
        token1 {
          id
        }
      }
    }
  '''%(pair_address, start_time)



  # Send the GraphQL request
  response = requests.post(uniswap_url, json={'query': query})

  # Parse the response JSON
  data = response.json()
  if data['data']['pairDayDatas'][0]['token0']['id'] == '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':
    pool_weth = float(data['data']['pairDayDatas'][0]['reserve0'])
  else:
    pool_weth = float(data['data']['pairDayDatas'][0]['reserve1'])

  if pool_weth:
    return pool_weth
  else:
    return 0


if __name__ == "__main__":
  h = get_trade_start("0x28a19dd48b732ce10a05e683ccfca4aa21ed29a1".lower(), 1679944235)
  print(h)
  v = get_weth_volume("0x28a19dd48b732ce10a05e683ccfca4aa21ed29a1".lower(), h)
  print(v)
  # h = get_pool_weth("0x04Ebc9a331ca43c933b1C76C5cFCfFcF4FdF433E", int(datetime.now().timestamp()))
  # print(h)
