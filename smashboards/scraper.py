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

def get_event_id_from_url(url):
  return int(url.split('/')[-2].split('.')[-1])

def get_players_for_event_page(event_id, soup, player_map):
  '''
  Parse page of event and build {swf name -> PlayerInfo} map
  '''
  table = soup.find("table", class_=get_table_class())
  rows = table.find_all("tr", class_=get_row_class())

  num_tags_found = 0

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
      player_map[username].add_tag(event_id, tag).add_characters(characters)
    else:
      player_map[username] = PlayerInfo(user_id, username).add_tag(event_id, tag).add_characters(characters)

  print "Tags found: {}".format(str(num_tags_found))

def parse_with_expected_prefix(line, prefix, thing_to_parse):
  if line.find(prefix) < 0:
    raise ValueError("Error parsing {} from line:\n{}\n".format(thing_to_parse, line))
  return line[len(prefix):].strip()

def parse_event_host(line):
  return parse_with_expected_prefix(line, 'Hosted By ', 'event host')

def parse_event_location(line):
  return parse_with_expected_prefix(line, '@ ', 'event location')

def parse_event_info(event_id, soup):
  event_name = soup.find("div", class_="titleBar").text.strip()
  detail_box = soup.find("div", id="eventDetails").find_all("div")[1]

  detail_box_text = detail_box.text.split('\n')
  ''' example value:
    [u'',
     u'Hosted By Atlas',
     u'Thursday, May 12, 2016 08:00 PM',
     u'@ Game Underground',
     u'',
     u'Melee',
     u'Double Elimination - Local',
     u'34 Players - 170 Points - $0 Entry Fee',
     u'',
     u'Posted By The-Jester',
     u'',
     u'',
     u'',
     u'']
  '''
  event_host = parse_event_host(detail_box_text[1])
  event_date = detail_box_text[2]
  event_location = parse_event_location(detail_box_text[3])

  detail_box_links = detail_box.find_all("a")
  ''' example value:
    [<a href="rankings/melee/league/events">Melee</a>,
     <a href="rankings/local.2/category">Local</a>,
     <a href="members/the-jester.292125/">The-Jester</a>]
  '''
  # sanity check for now, may support other games later
  if detail_box_links[0].text != 'Melee':
    raise ValueError("Expected first link to be game")
  if detail_box_links[1]['href'].split('/')[-1] != 'category':
    raise ValueError("Expected second link to be event category")
  if detail_box_links[2]['href'].split('/')[0] != 'members':
    raise ValueError("Expected third link to be to a user")

  event_category = detail_box_links[1].text
  event_uploader_id = int(detail_box_links[2]['href'].split('/')[1].split('.')[-1])

  return EventInfo(event_id, event_name, event_category, event_date, event_host, event_location, event_uploader_id)

def process_event(event_url, player_map):
  '''
  Parse all pages for event. We assume event_url is the first page of the event's results.
  '''
  page_url = event_url
  event_info = None
  event_id = get_event_id_from_url(page_url)

  while True:
    soup = get_soup(page_url)

    if not event_info:
      event_info = parse_event_info(event_id, soup)

    query_params = {k: v for k,v in [t.split('=') for t in page_url.split('?')[-1].split('&')]}
    page = query_params['page'] if 'page' in query_params else '1'
    print "Processing {} page {}".format(event_info.swf_event_name, page)

    get_players_for_event_page(event_id, soup, player_map)

    navdiv = soup.find("div", class_="PageNav")
    if navdiv is None: # only 1 page
      break

    last_button = navdiv.find_all("a")[-1]
    if last_button.text.find('Next') < 0: # last page: no 'Next >' button
      break

    page_url = path.join(get_base_url(), last_button['href'])

  return event_info

def main():
  pass

def print_usage_and_exit():
  # print "Usage: " + sys.argv[0] + " {} {} []"
  exit(1)

if __name__ == "__main__":
  main()
