import requests
import json
import random

PAGE_SIZE = 100

def get_twitch_paginated(url, main_property, info_key, sub_property_key, sub_property_values=[]):
    ret = {}
    cur_url = url

    while True:
        print "GET " + cur_url
        r = requests.get(cur_url)
        if r.status_code == 200:
            all_data = r.json()
        else:
            print "failed to get url " + cur_url
            break

        data = all_data[main_property] # should be a list

        ret["_total"] = all_data["_total"]

        if len(data) == 0:
            break

        ret.update( 
            {element[info_key][sub_property_key]: 
                { sub_property_value: element[info_key][sub_property_value] 
                  for sub_property_value in sub_property_values }
            for element in data }
        )

        cur_url = all_data["_links"]["next"]

    return ret


def get_follows(username):
    url = "https://api.twitch.tv/kraken/users/{}/follows/channels?limit={}&offset={}".format(username, PAGE_SIZE, 0)
    main_property = "follows"
    info_key = "channel"
    sub_property_key = "name"
    sub_property_values = ["game", "followers", "views"]

    return get_twitch_paginated(url, main_property, info_key, sub_property_key, sub_property_values)

def get_follows_list(username_list):
    return dict([(username, get_follows(username)) for username in username_list])

