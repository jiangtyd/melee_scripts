from bs4 import BeautifulSoup as BS
import requests
import re
import itertools
import sys
import os
import os.path as path
import shutil
import pickle
from model import PlayerInfo, EventInfo

TABLE_CLASS="resultsList"
ROW_CLASS="listRow"
BASE_URL = "http://smashboards.com/"
EVENTS_URL="http://smashboards.com/rankings/melee/league/events"

EXAMPLE_BRACKET="http://smashboards.com/rankings/im-not-yelling-melee-singles.5951/event?id=2"

def get_table_class():
  global TABLE_CLASS
  return TABLE_CLASS

def get_row_class():
  global ROW_CLASS
  return ROW_CLASS

def get_base_url():
  global BASE_URL
  return BASE_URL

# Webpage parsing
def get_soup(url):
  ''' 
  Get the soup object for this url
  '''
  r = requests.get(url)
  return BS(r.text, "lxml")

def get_character_from_url(url):
  return url.split('/')[-1].split('.')[0]

def get_players_for_tournament_page(soup, player_map):
  '''
  Parse page of tournament and build {swf name -> PlayerInfo} map
  '''
  table = soup.find("table", class_=get_table_class())
  rows = table.find_all("tr", class_=get_row_class())

  num_tags_found = 0
  num_new_tags_found = 0

  for row in rows:
    rank_td, tag_td, characters_td, earnings_td, points_td, username_td = row.find_all("td")

    # key for the map. skip if there is none
    username = username_td.text.strip()
    if len(username) == 0:
      continue

    num_tags_found += 1

    # href looks like 'rankings/a-rookie.139354/user?id=2'
    user_id = int(username_td.find_all("a")[-1]['href'].split('/')[1].split('.')[-1])

    tag = tag_td.text.strip()
    characters = [get_character_from_url(img['src']) for img in characters_td.find_all('img')]

    if username in player_map:
      player_map[username].add_tag(tag).add_characters(characters)
    else:
      num_new_tags_found += 1
      player_map[username] = PlayerInfo(user_id, username).add_tag(tag).add_characters(characters)

  print "Tags found: {}, new tags found: {}".format(str(num_tags_found), str(num_new_tags_found))

def get_players_for_tournament(tournament_url, player_map):
  '''
  Parse all pages for tournament
  '''
  page_url = tournament_url
  while True:
    soup = get_soup(page_url)

    query_params = {k: v for k,v in [t.split('=') for t in page_url.split('?')[-1].split('&')]}
    page = query_params['page'] if 'page' in query_params else '1'
    tournament_name = soup.find("div", class_="titleBar").text.strip()
    print "Processing {} page {}".format(tournament_name, page)

    get_players_for_tournament_page(soup, player_map)

    navdiv = soup.find("div", class_="PageNav")
    if navdiv is None: # only 1 page
      break

    last_button = navdiv.find_all("a")[-1]
    if last_button.text.find('Next') < 0: # last page: no 'Next >' button
      break

    page_url = path.join(get_base_url(), last_button['href'])

def main():
  pass

def print_usage_and_exit():
  # print "Usage: " + sys.argv[0] + " {} {} []"
  exit(1)

if __name__ == "__main__":
  main()
