from bs4 import BeautifulSoup as BS
import requests
import re
import itertools
import sys
import os
import os.path as path
import shutil
import pickle

######## BEGIN globals ########

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

######## END globals ########

######## BEGIN PlayerInfo ########
class PlayerInfo(object):
  def __init__(self, swf_player_id, swf_player_name):
    if swf_player_id is None or not isinstance(swf_player_id, int) or swf_player_id < 0:
      raise ValueError("swf player id should be nonnegative int")
    self.swf_player_id = swf_player_id
    self.set_swf_player_name(swf_player_name)
    self.tags = set()
    self.characters = set()

  def set_swf_player_name(self, swf_player_name):
    if swf_player_name is None or not isinstance(swf_player_name, unicode) or len(swf_player_name) == 0:
      raise ValueError("swf player name should be nonempty unicode string")
    self.swf_player_name = swf_player_name
    return self

  def add_tag(self, tag):
    if tag is None or not isinstance(tag, unicode) or len(tag) == 0:
      raise ValueError("tag should be nonempty unicode string")
    self.tags.add(tag)
    return self

  def del_tag(self, tag):
    if tag in self.tags:
      self.tags.remove(tag)
      return self
    else:
      raise ValueError("tag {} not in list of tags for player {}".format(tag, player.swf_player_name))

  def get_tags_sorted(self):
    return sorted(self.tags)

  def add_character(self, character):
    if character is None or not isinstance(character, str) or len(character) == 0:
      raise ValueError("character name should be nonempty unicode string")
    self.characters.add(character)
    return self

  def add_characters(self, character_iterable):
    for character in character_iterable:
      self.add_character(character)
    return self

  def del_character(self, character):
    if character in self.characters:
      self.characters.remove(character)
      return self
    else:
      raise ValueError("character {} not in list of characters for player {}"
          .format(character, player.swf_player_name))

  def get_characters_sorted(self):
    return sorted(self.characters)

  def __str__(self):
    return "swf_player_id: {}, swf_player_name: {}, tags: {}, characters: {}".format(
        self.swf_player_id, self.swf_player_name, str(self.tags), str(self.characters))

  def to_csv_row(self):
    return [
        self.swf_player_id, self.swf_player_name, ', '.join(self.characters)
      ] + sorted(self.tags, key=lambda t: len(t))

######## END PlayerInfo ########

######## BEGIN EventInfo ########
class Event(object):
    def __init__(self, swf_event_id, swf_event_name, category, date_str):
        if swf_event_id is None or not isinstance(swf_event_id, int) or swf_event_id < 0:
          raise ValueError("swf event id should be nonnegative int")
        self.swf_event_id = swf_event_id
        if swf_event_name is None or not isinstance(swf_event_name, unicode) or len(swf_event_name) == 0:
          raise ValueError("swf event name should be nonempty unicode string")
        self.swf_event_name = swf_event_name
        if category is None or not isinstance(category, str) or len(category) == 0:
          raise ValueError("event category should be nonempty string")
        self.category = category

        if date_str is None or not isinstance(date_str, str) or len(date_str) == 0:
          raise ValueError("event date should be passed in as nonempty string")
        try:
            self.date = date_str.strptime("%Y-%b-%d")
        except ValueError:
            raise ValueError("event date {} could not be parsed".format(date_str))

######## END EventInfo ########

# Webpage parsing
def get_soup(url):
  ''' 
  Get the soup object for this url
  '''
  r = requests.get(url)
  return BS(r.text, "lxml")

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
    characters = [img['title'] for img in characters_td.find_all('img')]

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
