import pair_finder
import scrapers
import weth_volume
from os.path import exists
from web3 import Web3
import time

def main(last_block, tokens_to_process, file_path="data/dumb_contracts.txt"):
  processed_tokens = 0
  block_range_end = last_block

  while processed_tokens < tokens_to_process:
    block_range_start = block_range_end - 1000
    current_list = pair_finder.get_uniswap_pairs(from_block=block_range_start, to_block=block_range_end)
    for pair_instance in current_list:

      tokens = [pair_instance['token0'].lower(), pair_instance['token1'].lower()]
      weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2".lower()
      #making sure it's a weth pair
      if weth in tokens:
        #identifying token address
        for token in tokens:
          if token != weth:
            token_address = token

        print(f"Checking {token_address} at pair{pair_instance['pair_address']}")
        #getting contracts and abis
        token_contract = scrapers.get_contract(token_address)
        pair_contract = scrapers.get_contract(pair_instance['pair_address'])


        #Determine when trading started
        trade_start_time = weth_volume.get_trade_start(pair_instance['pair_address'], int(pair_instance["timestamp"])-(24*60*60))
        #Determine 24 hour trading volume
        traded_volume = weth_volume.get_weth_volume(pair_instance['pair_address'], trade_start_time)

        if token_contract and pair_contract:
          text_dump = "\n\n!!!!DIVIDER!!!!"
          text_dump = text_dump + f"\n\nTOKEN_ADDRESS:\n{token_address}"
          text_dump = text_dump + f"\n\nWETH_TRADE:\n{traded_volume}"
          text_dump = text_dump + f"\n\nCREATION_TIME:\n{pair_instance['timestamp']}"
          text_dump = text_dump + f"\n\nLAUNCH_TIME:\n{trade_start_time}"
          text_dump = text_dump + "\n\n!!!!TOKEN_CONTRACT!!!!\n\n"
          text_dump = text_dump + token_contract
          text_dump = text_dump + "\n\n!!!!PAIR_CONTRACT!!!!\n\n"
          text_dump = text_dump + pair_contract

          processed_tokens += 1

          if exists(file_path):
            with open(file_path, 'a') as file:
              file.write(text_dump)
          else:
            with open(file_path, 'w') as file:
              file.write(text_dump)
          break
        time.sleep(1)

    block_range_end = block_range_start - 1

if __name__ == "__main__":
  main(16933754, 1000)