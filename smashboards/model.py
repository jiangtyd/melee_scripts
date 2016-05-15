from datetime import datetime, date

def check_nonnegative_int(var, var_name):
  if var is None or not isinstance(var, int) or var < 0:
      raise ValueError("{} should be nonnegative int".format(var_name))

def check_nonempty_string(var, var_name):
  if var is None or (not isinstance(var, unicode) and not isinstance(var, str)) or len(var) == 0:
      raise ValueError("{} should be nonempty string or unicode string".format(var_name))

class PlayerInfo(object):
  def __init__(self, swf_player_id, swf_player_name):
    check_nonnegative_int(swf_player_id, "swf player id")
    self.swf_player_id = swf_player_id
    self.set_swf_player_name(swf_player_name)
    self.tags = dict()
    self.characters = set()

  def set_swf_player_name(self, swf_player_name):
    check_nonempty_string(swf_player_name, "swf player name")
    self.swf_player_name = unicode(swf_player_name)
    return self

  def add_tag(self, event_id, tag):
    check_nonempty_string(tag, "tag")
    check_nonnegative_int(event_id, "swf event id")
    self.tags[event_id] = tag
    return self

  def del_tag(self, event_id):
    if event_id in self.tags:
      self.tags.remove(event_id)
      return self
    else:
      raise ValueError("player {} did not have a tag in event {}".format(player.swf_player_name, event_id))

  def get_tags_sorted(self):
    return sorted(self.tags.values())

  melee_characters = set([
    'fox', 'falco', 'marth', 'sheik',
    'falcon', 'peach', 'jigglypuff', 'ic',
    'samus', 'ganon', 'luigi', 'drmario',
    'link', 'pikachu', 'yoshi', 'dk',
    'roy', 'mario', 'zelda', 'gamewatch',
    'ylink', 'kirby', 'ness', 'bowser',
    'mewtwo', 'pichu'])

  def add_character(self, character):
    check_nonempty_string(character, "character name")
    if character not in PlayerInfo.melee_characters:
      raise ValueError("'{}' is not a valid melee character".format(character))

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
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return u"swf_player_id: {}, swf_player_name: {}, tags: {}, characters: {}".format(
        self.swf_player_id, self.swf_player_name, unicode(self.tags), unicode(self.characters))

  def to_csv_row(self):
    return [
        self.swf_player_id, self.swf_player_name, ', '.join(self.characters)
      ] + sorted(self.tags, key=lambda t: len(t))

class EventInfo(object):
  event_categories = set([
    'Premier', 'Global', 'International',
    'National', 'Regional', 'Local',
    'Large Local', 'Pools', 'Teams',
    'Unranked', 'Online'])

  def __init__(self, swf_event_id, swf_event_name, category, date_or_date_str, host, location, uploader_id):
    check_nonnegative_int(swf_event_id, "swf event id")
    check_nonempty_string(swf_event_name, "swf event name")
    check_nonempty_string(category, "event category")
    if category not in EventInfo.event_categories:
      raise ValueError("'{}' is not a valid swf event category".format(category))
    check_nonempty_string(host, "event host")
    check_nonempty_string(location, "event location")
    check_nonnegative_int(uploader_id, "event uploader id")
    self.swf_event_id = swf_event_id
    self.swf_event_name = unicode(swf_event_name)
    self.category = category
    self.host = unicode(host)
    self.location = unicode(location)
    self.uploader_id = uploader_id

    if date_or_date_str is None:
      raise ValueError("event date should not be None")
    elif isinstance(date_or_date_str, date):
      self.date = date_or_date_str
    elif isinstance(date_or_date_str, unicode) or isinstance(date_or_date_str, str):
      self.date = parse_date_str(date_or_date_str)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return u"swf_event_id: {}, swf_event_name: {}, category: {}, date: {}, host: {}, location: {}, uploader id: {}".format(self.swf_event_id, self.swf_event_name, self.category, self.date, self.host, self.location, self.uploader_id)

def parse_date_str(date_str):
  ret_date = None

  if len(date_str) == 0:
    raise ValueError("event date string should be nonempty")

  try: # format on brackets page
    ret_date = datetime.strptime(date_str, "%Y-%b-%d").date()
  except ValueError:
    pass

  try: # format on an individual bracket's page
    ret_date = datetime.strptime(date_str, "%A, %B %d, %Y %I:%M %p").date()
  except ValueError:
    pass

  if ret_date == None: # neither succeeded
    raise ValueError("event date {} could not be parsed".format(date_str))
  else:
    return ret_date

