import requests
import config
import json
from datetime import datetime, timedelta
import time


def get_liquidity_removed(api_key, address):
  url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={api_key}'
  response = requests.get(url)
  transactions = response.json()['result']
  function_names = []
  for transaction in transactions:
    function_names.append(transaction['functionName'])
  for function_name in function_names:
    if "removeliquidity" in function_name.lower():
      return True
    
  return False

def preprocess_text(filepath):
  """
  Returns a list of dicts
  """
  divider = "\n\n!!!!DIVIDER!!!!\n\n"
  with open(filepath, "r", encoding="utf8") as f:
    file_contents = f.read()

  main_sections = file_contents.split(divider)

  parsed_data = []
  for section in main_sections[1:]:
    parsed_section = {}
    details, contracts = section.split('\n\n!!!!TOKEN_CONTRACT!!!!\n\n')
    token_contract, pair_contract = contracts.split("\n\n!!!!PAIR_CONTRACT!!!!\n\n")
    for subsection in details.split("\n\n"):
      key, value = subsection.split(":\n")
      parsed_section[key.lower()] = value
    parsed_section['token_contract'] = token_contract
    parsed_section['pair_contract'] = pair_contract
    parsed_data.append(parsed_section)

  return parsed_data 

if __name__ == "__main__":
  data_path = 'data/dumb_contracts.txt'
  preprocessed_data = preprocess_text(data_path)

  etherscan_counter = 0
  overall_counter = 0
  round_end_time = datetime.now() + timedelta(seconds=1, milliseconds=100)
  print("Starting")
  for pair_details in preprocessed_data:
    needs_update = True
    while needs_update:
      try:
        pair_details['liquidity_removed'] = get_liquidity_removed(config.etherscan_api_key, pair_details["token_address"])
        needs_update = False
      except Exception as e:
        print(e)
        time.sleep(10)
    etherscan_counter += 1
    overall_counter += 1
    if etherscan_counter == 5:
      while datetime.now() < round_end_time:
        pass
      etherscan_counter = 0
      round_end_time = datetime.now() + timedelta(seconds=1, milliseconds=100)
    
    if overall_counter%10 == 0:
      print(f"Done {overall_counter} records!")


  with open("data/dumb_contracts.json", "w") as outfile:
    json.dump(preprocessed_data, outfile)


