import mysql.connector
from mysql.connector import errorcode
from config.config import Config
from model import PlayerInfo, EventInfo
from datetime import date
from itertools import chain

def get_connection():
  config = Config()
  mysql_config = {
    'user': config.get_db_user(),
    'password': config.get_db_password(),
    'host': config.get_db_host(),
    'database': config.get_db_name()
  }
  return mysql.connector.connect(**mysql_config)

def check_list_type(input_list, desired_type):
  assert isinstance(input_list, list) and len(input_list) >= 1
  for element in input_list:
    assert isinstance(element, desired_type)

def build_paren_s_list(n):
  return '(' + ', '.join(['%s' for i in xrange(n)]) + ')'

def build_values_str(num_cols, num_rows):
  return ', '.join([build_paren_s_list(num_cols) for i in xrange(num_rows)])

def build_in_clause_str(num_in):
  return build_paren_s_list(num_in)

class Repository(object):
  def __init__(self, cnx):
    self.cnx = cnx
    self.cursor = cnx.cursor()

  def execute_statement(self, build_func, data):
    if len(data) == 0:
      raise ValueError("data should be nonempty")
    print "build_func(len(data)) =", build_func(len(data))
    if isinstance(data[0], list) or isinstance(data[0], tuple):
      flattened_data = list(chain.from_iterable(data))
    else:
      flattened_data = data
    print "flattened data =", flattened_data
    self.cursor.execute(build_func(len(data)), flattened_data)

class PlayerRepository(Repository):
  def __init__(self, cnx):
    super(PlayerRepository, self).__init__(cnx)

  def __insert_player_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['INSERT INTO `players` (`id`, `username`) VALUES']
      + [build_values_str(2, n)]
      # if a SWF user changes his/her username
      + ['ON DUPLICATE KEY UPDATE `username`=VALUES(`username`)']
    ) + ';'

  def __insert_player_tag_map_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['INSERT INTO `player_tag_map` (`player_id`, `tag`, `event_id`) VALUES']
      + [build_values_str(3, n)]
      # if a player's tag at an event is somehow changed...
      + ['ON DUPLICATE KEY UPDATE `tag`=VALUES(`tag`)']
    ) + ';'

  # assume that players never remove characters that they've once played
  def __insert_player_character_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['INSERT IGNORE INTO `characters` (`player_id`, `character_name`) VALUES']
      + [build_values_str(2, n)]
    ) + ';'

  # players = list of PlayerInfo
  def save_players(self, players):
    check_list_type(players, PlayerInfo)

    player_id_name = [(player.swf_player_id, player.swf_player_name)
      for player in players]
    self.execute_statement(self.__insert_player_statement, player_id_name)

    player_tags = []
    for player in players:
      player_tags.extend([(player.swf_player_id, player.tags[event_id], event_id) for event_id in player.tags])
    self.execute_statement(self.__insert_player_tag_map_statement, player_tags)

    player_characters = []
    for player in players:
      player_characters.extend([(player.swf_player_id, character) for character in player.characters])
    self.execute_statement(self.__insert_player_character_statement, player_characters)

    self.cnx.commit()

  def __select_player_by_id_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['SELECT `id`, `username` FROM `players`']
      + ['WHERE `id` IN']
      + [build_in_clause_str(n)]
    ) + ';'

  def __select_player_tags_by_id_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['SELECT `player_id`, `tag`, `event_id` FROM `player_tag_map`']
      + ['WHERE `player_id` IN']
      + [build_in_clause_str(n)]
    ) + ';'

  def __select_player_characters_by_id_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['SELECT `player_id`, `character_name` FROM `characters`']
      + ['WHERE `player_id` IN']
      + [build_in_clause_str(n)]
    ) + ';'

  def get_player_by_id(self, swf_player_id):
    return self.get_players_by_ids([swf_player_id])[swf_player_id]

  def get_players_by_ids(self, swf_player_id_list):
    ret_players = {}

    self.execute_statement(self.__select_player_by_id_statement, swf_player_id_list)
    for (swf_player_id, swf_player_name) in self.cursor:
      # print ">>> select from players >>>", swf_player_id, swf_player_name
      ret_players[swf_player_id] = PlayerInfo(swf_player_id, swf_player_name)

    self.execute_statement(self.__select_player_tags_by_id_statement, swf_player_id_list)
    for (swf_player_id, tag, swf_event_id) in self.cursor:
      # print ">>> select from player_tag_map >>>", swf_player_id, tag, swf_event_id
      ret_players[swf_player_id].add_tag(swf_event_id, tag)

    self.execute_statement(self.__select_player_characters_by_id_statement, swf_player_id_list)
    for (swf_player_id, character) in self.cursor:
      # print ">>> select from characters >>>", swf_player_id, character
      ret_players[swf_player_id].add_character(character)

    return ret_players


class EventRepository(Repository):
  def __init__(self, cnx):
    super(EventRepository, self).__init__(cnx)

  def __insert_event_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['INSERT INTO `events` (`id`, `event_name`, `category`, `event_date`) VALUES']
      + [build_values_str(4, n)]
      # if a SWF user changes his/her username
      + ['ON DUPLICATE KEY UPDATE']
      + ['`event_name`=VALUES(`event_name`),']
      + ['`category`=VALUES(`category`),']
      + ['`event_date`=VALUES(`event_date`)']
    ) + ';'

  def save_events(self, events):
    check_list_type(events, EventInfo)

    event_info_row = [(event.swf_event_id, event.swf_event_name, event.category, event.date) for event in events]
    self.execute_statement(self.__insert_event_statement, event_info_row)

    self.cnx.commit()

  def __select_event_by_id_statement(self, n):
    assert isinstance(n, int) and n > 0
    return ' '.join(
      ['SELECT `id`, `event_name`, `category`, `event_date` FROM `events`']
      + ['WHERE `id` IN']
      + [build_in_clause_str(n)]
    ) + ';'

  def get_event_by_id(self, swf_event_id):
    return self.get_events_by_ids([swf_event_id])[swf_event_id]

  def get_events_by_ids(self, swf_event_id_list):
    ret_events = {}

    self.execute_statement(self.__select_event_by_id_statement, swf_event_id_list)
    for (swf_event_id, swf_event_name, category, date) in self.cursor:
      # print ">>> select from events >>>", swf_event_id, swf_event_name, category, date
      ret_events[swf_event_id] = EventInfo(swf_event_id, swf_event_name, category, date)

    return ret_events
