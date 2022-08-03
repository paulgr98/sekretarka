import json
import datetime as dt
import os
import hashlib


def get_data():
    # if the file doesn't exist, create it
    if not os.path.isfile('matches.json'):
        with open('matches.json', 'w') as f:
            json.dump({}, f, indent=4)
    # read the file
    with open('matches.json', 'r') as f:
        data = json.load(f)
    return data


def save_users_match_for_today(guid_id, user_id, match_id):
    today = dt.datetime.now().strftime('%d.%m.%Y')
    data = get_data()

    # create hash with guild id and today's date to user as key and match id as value
    hash_key = hashlib.sha1(str(guid_id).encode('utf-8') + str(today).encode('utf-8')).hexdigest()

    # if the user doesn't have any match for hash, create a new entry
    if hash_key not in data:
        data[hash_key] = {}
    # add the user id and match id to the hash
    data[hash_key][user_id] = match_id
    # save the data
    with open('matches.json', 'w') as f:
        json.dump(data, f, indent=4)


def get_users_match_for_today(guid_id, user_id):
    today = dt.datetime.now().strftime('%d.%m.%Y')
    data = get_data()

    # create hash with guild id and today's date to user as key and match id as value
    hash_key = hashlib.sha1(str(guid_id).encode('utf-8') + str(today).encode('utf-8')).hexdigest()

    # if the user doesn't have any match for hash, return None
    if hash_key not in data or user_id not in data[hash_key]:
        return None
    # return the match id
    return data[hash_key][user_id]


def get_user_top_match(user_id):
    data = get_data()
    # search for the user id in every hash
    ship_count_dict = {}
    for hash_key in data:
        if user_id in data[hash_key]:
            ship = data[hash_key][user_id]
            if ship not in ship_count_dict:
                ship_count_dict[ship] = 1
            else:
                ship_count_dict[ship] += 1
    # return the most common match
    return max(ship_count_dict, key=ship_count_dict.get)
