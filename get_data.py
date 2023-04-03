import pair_finder
import scrapers
import weth_volume
from os.path import exists
import time
import logging
import traceback

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('logs/dumb_contracts.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate=False

def main(last_block, tokens_to_process, file_path="data/dumb_contracts.txt"):
  processed_tokens = 0
  block_range_end = last_block
  pair_address = 0
  logger.info("STARTING")

  while processed_tokens < tokens_to_process:
    block_range_start = block_range_end - 1000
    try:
      current_list = pair_finder.get_uniswap_pairs(from_block=block_range_start, to_block=block_range_end)
      for pair_instance in current_list:
        try:

          tokens = [pair_instance['token0'].lower(), pair_instance['token1'].lower()]
          weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2".lower()
          pair_address = pair_instance['pair_address']
          #making sure it's a weth pair
          if weth in tokens:
            #identifying token address
            for token in tokens:
              if token != weth:
                token_address = token

            #getting contracts and abis
            token_contract = scrapers.get_contract(token_address)
            pair_contract = scrapers.get_contract(pair_instance['pair_address'])


            #Determine when trading started
            trade_start_time = weth_volume.get_trade_start(pair_instance['pair_address'], int(pair_instance["timestamp"])-(24*60*60))
            #Determine 24 hour trading volume
            if trade_start_time:
              traded_volume = weth_volume.get_weth_volume(pair_instance['pair_address'], trade_start_time)
              #Get pool weth amount 3 days later
              weth_size = weth_volume.get_pool_weth(pair_instance['pair_address'], trade_start_time+(3*24*60*60))

              if token_contract and pair_contract:
                text_dump = "\n\n!!!!DIVIDER!!!!"
                text_dump = text_dump + f"\n\nTOKEN_ADDRESS:\n{token_address}"
                text_dump = text_dump + f"\n\nPAIR_ADDRESS:\n{pair_instance['pair_address']}"
                text_dump = text_dump + f"\n\nWETH_TRADE:\n{traded_volume}"
                text_dump = text_dump + f"\n\nWETH_LEFT:\n{weth_size}"
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
            time.sleep(0.7)
        except Exception as e:
          logger.error(pair_address)
          logger.error(e)
          logger.debug(traceback.format_exc())

      block_range_end = block_range_start - 1
      logger.info(f"NEW BLOCK RANGE ENDING ON {block_range_end}")
    except Exception as e:
      logger.error(e)
      logger.error(pair_address)
      logger.debug(traceback.format_exc())
      quit()

if __name__ == "__main__":
  main(16347900, 23000)