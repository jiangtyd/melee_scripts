import requests

def get_entrants(tournament_name, event_name):
    url = 'https://api.smash.gg/tournament/{}/event/{}?expand[0]=entrants'.format(tournament_name, event_name)
    return requests.get(url).json()['entities']['entrants']

def get_name_id_map(entrants):
    return {e['name']: e['id'] for e in entrants}

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

