import mysql.connector
from mysql.connector import errorcode
from config.config import Config
from model import PlayerInfo, EventInfo

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
  def save_players_at_event(self, players, event):
    __check_list_type(players, PlayerInfo)
    assert isInstance(event, EventInfo)

    player_id_name = [(player.swf_player_id, player.swf_player_name)
      for player in players]
    self.execute_statement(__insert_player_statement, player_id_name)

    player_tags = [(player.swf_player_id, tag, event.swf_event_id) for tag in player.tags for player in players]
    self.execute_statement(__insert_player_tag_map_statement, player_tags)

    player_characters = [(player.swf_player_id, character) for character in player.characters for player in players]
