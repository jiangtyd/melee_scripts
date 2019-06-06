import csv
import re
import requests
import sys

def get_entrants(tournament_name, event_name):
    url = 'https://api.smash.gg/tournament/{}/event/{}?expand[0]=entrants'.format(tournament_name, event_name)
    return requests.get(url).json()['entities']['entrants']

def get_name_id_map(entrants):
    return {e['name']: e['id'] for e in entrants}

def import_seeding_csv(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        names = []
        short_names = []
        tiers = []
        for row in reader:
            names.append(row['Entrant'].decode('utf-8'))
            short_names.append(row['Player Short GamerTag'].decode('utf-8'))
            tier = int(row['Tier']) if row['Tier'] != '' else 0
            tiers.append(tier)
        return names, short_names, tiers

payload_regex = re.compile(r'"params":\{"data":(\[.*\])\}')
def build_curl_request(curl_file_name, id_skill_json):
    curl_req = ''
    with open(curl_file_name, 'r') as fin:
        curl_req = fin.read()
    return re.sub(r'"params":\{"data":(\[.*\])\}', r'"params":{"data":' + id_skill_json + '}', curl_req)

def import_name_column(name_column):
    return name_column.splitlines()

# expect: smashgg tier (top tier = 10, etc)
def import_tier_column(tier_column):
    return tier_column.splitlines()

def import_id_column(id_column):
    return id_column.splitlines()

def get_id_skill_json(names, skills, name_id_map):
    id_skill_pairs = zip([name_id_map[name] for name in names], skills)
    return str([{"entrantId": i[0], "skill": int(i[1])} for i in id_skill_pairs]).replace("'", '"')

def get_id_skill_json_3(names, short_names, skills, name_id_map):
    id_skill_pairs = zip([name_id_map[name] if name in name_id_map else name_id_map[short_name] for name, short_name in zip(names, short_names)], skills)
    return str([{"entrantId": i[0], "skill": int(i[1])} for i in id_skill_pairs]).replace("'", '"')

def get_id_skill_json_2(ids, skills):
    id_skill_pairs = zip(ids, skills)
    return str([{"entrantId": int(i[0]), "skill": int(i[1])} for i in id_skill_pairs]).replace("'", '"')

def create_seeding_request(tournament_name, event_name, seeding_csv_file, curl_file):
    names, short_names, tiers = import_seeding_csv(seeding_csv_file)
    name_id_map = get_name_id_map(get_entrants(tournament_name, event_name))
    id_skill_json = get_id_skill_json_3(names, short_names, tiers, name_id_map)
    return build_curl_request(curl_file, id_skill_json)

def main():
    print create_seeding_request(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == '__main__':
    main()
