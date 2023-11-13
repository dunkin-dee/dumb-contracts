import json

old_file_path = "data/final_data.json"
final_file_path = "data/final_final_data.json"

if __name__ == "__main__":
    with open(old_file_path, "r") as json_file:
        old_data = json.load(json_file)
    processed_pairs = []
    new_data = []

    for pair_info in old_data:
        if pair_info["pair_address"] not in processed_pairs:
            new_data.append(pair_info)
            processed_pairs.append(pair_info["pair_address"])

    with open(final_file_path, "w") as json_file:
        json.dump(new_data, json_file)

    print("Done")
