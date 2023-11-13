import pool
import json
from os.path import exists
import traceback
import shutil

if __name__ == "__main__":
    old_file_path = "data/preprocessed_contracts.json"
    temp_file_path = "data/final_data_temp.json"
    new_file_path = "data/final_data.json"
    failed_pairs_path = "data/failed_pairs.json"

    with open(old_file_path, "r") as json_file:
        old_data = json.load(json_file)

    if exists(new_file_path):
        with open(new_file_path, "r") as json_file:
            new_data = json.load(json_file)

    else:
        new_data = []

    if exists(failed_pairs_path):
        with open(failed_pairs_path, "r") as json_file:
            failed_pairs = json.load(json_file)

    else:
        failed_pairs = []

    already_processed_pairs = []
    for pair_info in new_data:
        already_processed_pairs.append(pair_info["pair_address"])

    new_data_len = len(new_data)
    saving_counter = 0

    print(f"{new_data_len + len(failed_pairs)} pairs saved")
    save_activated = False

    for pair_info in old_data:
        saving_counter += 1
        pair_address = pair_info["pair_address"]
        if (
            (pair_address not in already_processed_pairs)
            and (pair_address not in failed_pairs)
            and (saving_counter >= 27000)
        ):
            save_activated = True
            try:
                opening_hourly_prices = pool.get_hourly_pool_reserves(pair_address)
                launch_time, addliquidity_hash = pool.get_addliquidity_hash(
                    pair_address=pair_address
                )
                decoded_data = pool.get_addliquidity_decoded(addliquidity_hash)
                token_decimals, token_amount, eth_amount = pool.get_token_and_eth_added(
                    decoded_data=decoded_data
                )

                pair_info["opening_hour_prices"] = opening_hourly_prices
                pair_info["launch_time"] = launch_time
                pair_info["tokens_added"] = token_amount
                pair_info["eth_added"] = eth_amount
                pair_info["token_decimals"] = token_decimals
                pair_info["method"] = decoded_data["method"]

                new_data.append(pair_info)
            except Exception as e:
                print(pair_address)
                failed_pairs.append(pair_address)
                print(traceback.format_exc())
                # print(e)

        print(saving_counter)

        if saving_counter % 100 == 0 and save_activated:
            with open(temp_file_path, "w") as json_file:
                json.dump(new_data, json_file)
            shutil.copyfile(temp_file_path, new_file_path)
            with open(failed_pairs_path, "w") as json_file:
                json.dump(failed_pairs, json_file)
            print(f"Now working on {saving_counter+1}")

    with open(temp_file_path, "w") as json_file:
        json.dump(new_data, json_file)
    shutil.copyfile(temp_file_path, new_file_path)
    with open(failed_pairs_path, "w") as json_file:
        json.dump(failed_pairs, json_file)
    print(f"Now working on {saving_counter+1}")
