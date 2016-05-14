import mysql.connector
from mysql.connector import errorcode
from config.config import Config
from model import PlayerInfo, EventInfo
from datetime import date

def get_connection():
  config = Config()
  mysql_config = {
    'user': config.get_db_user(),
    'password': config.get_db_password(),
    'host': config.get_db_host(),
    'database': config.get_db_name()
  }
  return mysql.connector.connect(**mysql_config)

def __check_list_type(self, input_list, desired_type):
  assert isInstance(input_list, list) and len(input_list) >= 1
  for element in input_list:
    assert isInstance(element, desired_type)

class Repository(object):
  def __init__(cnx):
    self.cnx = cnx
    self.cursor = cnx.cursor()

  def execute_statement(self, build_func, data):
    self.cursor.execute(self.build_func(len(data)), data)

class PlayerRepository(Repository):
  def __init__(cnx):
    super(PlayerRepository, self).__init__(cnx)

  def __insert_player_statement(self, n):
    assert isInstance(n, int) and n > 0
    return ' '.join(
      ['INSERT INTO `players` (`id`, `username`) VALUES']
      + ['(%d, %ls)' for i in xrange(n)]
      # if a SWF user changes his/her username
      + ['ON DUPLICATE KEY UPDATE `username`=VALUES(`username`)']
    ) + ';'

  def __insert_player_tag_map_statement(self, n):
    assert isInstance(n, int) and n > 0
    return ' '.join(
      ['INSERT INTO `player_tag_map (`player_id`, `tag`, `event_id`) VALUES']
      + ['(%d, %ls, %d)' for i in xrange(n)]
      # if a player's tag at an event is somehow changed...
      + ['ON DUPLICATE KEY UPDATE `tag`=VALUES(`tag`)']
    ) + ';'

  # assume that players never remove characters that they've once played
  def __insert_player_character_statement(self, n):
    assert isInstance(n, int) and n > 0
    return ' '.join(
      ['INSERT IGNORE INTO `characters` (`player_id`, `character_name`) VALUES']
      + ['(%d, %s)' for i in xrange(n)]
    ) + ';'

  # players = list of PlayerInfo
  def save_players(self, players):
    __check_list_type(players, PlayerInfo)

    player_id_name = [(player.swf_player_id, player.swf_player_name)
      for player in players]
    self.execute_statement(__insert_player_statement, player_id_name)

    player_tags = [(player.swf_player_id, player.tags[event_id], event_id) for event_id in player.tags for player in players]
    self.execute_statement(__insert_player_tag_map_statement, player_tags)

    player_characters = [(player.swf_player_id, character) for character in player.characters for player in players]
    self.execute_statement(__insert_player_character_statement, player_characters)

class EventRepository(Repository):
  def __init__(cnx):
    super(EventRepository, self).__init__(cnx)

  def __insert_event_statement(self, n):
    assert isInstance(n, int) and n > 0
    return ' '.join(
      ['INSERT INTO `events` (`id`, `event_name`, `category`, `event_date`) VALUES']
      + ['(%d, %ls, %s, %s)' for i in xrange(n)]
      # if a SWF user changes his/her username
      + ['ON DUPLICATE KEY UPDATE']
      + ['`event_name`=VALUES(`event_name`),']
      + ['`category`=VALUES(`category`),']
      + ['`event_date`=VALUES(`event_date`),']
    ) + ';'

  def save_events(self, events):
    __check_list_type(players, EventInfo)

    event_info_row = [(event.swf_event_id, event.swf_event_name, event.category, event.date) for event in events]
    self.execute_statement(__insert_event_statement, event_info_row)

