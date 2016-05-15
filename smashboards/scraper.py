from bs4 import BeautifulSoup as BS
import requests
import re
import itertools
import sys
import os
import os.path as path
import shutil
import pickle
from urlparse import urlparse, parse_qs
import argparse

from model import PlayerInfo, EventInfo
import db

EVENTS_URL="http://smashboards.com/rankings/melee/league/events"
EXAMPLE_BRACKET="http://smashboards.com/rankings/im-not-yelling-melee-singles.5951/event?id=2"

def get_results_table_class():
  return "resultsList"

def get_events_table_class():
  return "eventsList"

def get_row_class():
  return "listRow"

def get_base_url():
  return "http://smashboards.com/"

# Webpage parsing
def get_soup(url):
  ''' 
  Get the soup object for this url
  '''
  print 'Processing page', url
  r = requests.get(url)
  return BS(r.text, "lxml")

def get_character_from_url(url):
  return url.split('/')[-1].split('.')[0]

def get_event_id_from_url(url):
  return int(url.split('/')[-2].split('.')[-1])

def get_players_for_event_page(event_id, soup):
  '''
  Parse page of event and build {swf name -> PlayerInfo} map
  '''
  table = soup.find("table", class_=get_results_table_class())
  rows = table.find_all("tr", class_=get_row_class())

  num_tags_found = 0

  player_list = []

  for row in rows:
    # skip results claim rows
    if row.find("td", class_="resultClm"):
      continue

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

    player_info = PlayerInfo(user_id, username).add_tag(event_id, tag).add_characters(characters)
    print "Found player", player_info

    player_list.append(player_info)

  print "Tags found: {}".format(str(num_tags_found))

  return player_list

def parse_with_expected_prefix(line, prefix, thing_to_parse):
  if line.find(prefix) < 0:
    raise ValueError("Error parsing {} from line:\n{}\n".format(thing_to_parse, line))
  return line[len(prefix):].strip()

def parse_event_host(line):
  return parse_with_expected_prefix(line, 'Hosted By ', 'event host')

def parse_event_location(line):
  return parse_with_expected_prefix(line, '@ ', 'event location')

# in this method, we make assumptions about how the event info box looks,
# so we try to check a bunch of them
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

  event_category = detail_box_links[1].text.strip()
  event_uploader_id = int(detail_box_links[2]['href'].split('/')[1].split('.')[-1])
  event_uploader_name = detail_box_links[2].text.strip()

  return event_uploader_name, EventInfo(event_id, event_name, event_category, event_date, event_host, event_location, event_uploader_id)

def get_page_from_url(url):
  query_params = parse_qs(urlparse(url).query)
  return query_params['page'][0] if 'page' in query_params else '1'

# TODO use data-page / data-last in the PageNav div for page-related stuff?
def get_next_page_url(soup):
  navdiv = soup.find("div", class_="PageNav")
  if navdiv is None: # only 1 page
    return None

  last_button = navdiv.find_all("a")[-1]
  if last_button.text.find('Next') < 0: # last page: no 'Next >' button
    return None

  return path.join(get_base_url(), last_button['href'])

def process_event(event_url):
  '''
  Parse all pages for event. We assume event_url is the first page of the event's results.
  '''
  page_url = event_url
  event_uploader_name = None
  event_info = None
  event_id = get_event_id_from_url(page_url)

  player_list = []

  # breaks when there's no next page
  while page_url:
    page = get_page_from_url(page_url)

    soup = get_soup(page_url)
    if not event_info:
      event_uploader_name, event_info = parse_event_info(event_id, soup)

    # skip teams due to "tag" weirdness
    if event_info.category == 'Teams':
      print "Skipping teams event..."
      break

    print u"Processing {} page {}".format(unicode(event_info.swf_event_name), page)

    player_list.extend(get_players_for_event_page(event_id, soup))

    page_url = get_next_page_url(soup)

  return event_uploader_name, event_info, player_list

def get_event_urls(soup):
  table = soup.find("table", class_=get_events_table_class())
  rows = table.find_all("tr", class_=get_row_class())

  event_urls = []

  for row in rows:
    date_td, category_td, name_td, players_td, earnings_td, points_td, uploader_td = row.find_all("td")
    event_path = name_td.find("a")['href']
    event_urls.append(path.join(get_base_url(), event_path))

  return event_urls

def scrape_events(event_list_url=EVENTS_URL, page_limit=0, rescrape=False):
  page_url = event_list_url

  cnx = db.get_connection()

  player_repo = db.PlayerRepository(cnx)
  event_repo = db.EventRepository(cnx)

  # breaks when there's no next page
  while page_url:
    page = get_page_from_url(page_url)
    if page_limit > 0 and int(page) > page_limit:
      print "Page {} passed page limit {}; finishing up.".format(page, page_limit)
      break

    print "Processing Melee events page {}".format(page)

    soup = get_soup(page_url)

    event_urls = get_event_urls(soup)

    # filter out already scraped urls if rescrape=False
    if not rescrape:
      event_ids = [get_event_id_from_url(url) for url in event_urls]
      existing_events = event_repo.get_events_by_ids(event_ids)
      event_urls = [url for url in event_urls if get_event_id_from_url(url) not in existing_events]

    for event_url in event_urls:
      event_uploader_name, event_info, player_list = process_event(event_url)
      # add uploader to db
      player_repo.save_player(PlayerInfo(event_info.uploader_id, event_uploader_name))
      event_repo.save_event(event_info)
      if len(player_list) > 0:
        player_repo.save_players_full(player_list)

    page_url = get_next_page_url(soup)

def main():
  parser = argparse.ArgumentParser(prog=sys.argv[0], description='Scrape Smashboards brackets into a mysql db.')
  parser.add_argument('-l', '--limit', default=0)
  parser.add_argument('-r', '--rescrape', action='store_true', default=False)
  args = vars(parser.parse_args(sys.argv[1:]))
  page_limit = int(args['limit'])
  rescrape = args['rescrape']

  print 'limit = ', page_limit
  print 'rescrape = ', rescrape

  scrape_events(page_limit=page_limit, rescrape=rescrape)

if __name__ == "__main__":
  main()
