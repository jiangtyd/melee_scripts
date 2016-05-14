from datetime import datetime, date

class PlayerInfo(object):
  def __init__(self, swf_player_id, swf_player_name):
    if swf_player_id is None or not isinstance(swf_player_id, int) or swf_player_id < 0:
      raise ValueError("swf player id should be nonnegative int")
    self.swf_player_id = swf_player_id
    self.set_swf_player_name(swf_player_name)
    self.tags = dict()
    self.characters = set()

  def set_swf_player_name(self, swf_player_name):
    if swf_player_name is None or not isinstance(swf_player_name, unicode) or len(swf_player_name) == 0:
      raise ValueError("swf player name should be nonempty unicode string")
    self.swf_player_name = swf_player_name
    return self

  def add_tag(self, event_id, tag):
    if tag is None or not isinstance(tag, unicode) or len(tag) == 0:
      raise ValueError("tag should be nonempty unicode string")
    if event_id is None or not isinstance(event_id, int) or event_id < 0:
      raise ValueError("swf event id should be nonnegative int")
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

  def add_character(self, character):
    if character is None or not isinstance(character, unicode) or len(character) == 0:
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

class EventInfo(object):
    def __init__(self, swf_event_id, swf_event_name, category, date_or_date_str):
        if swf_event_id is None or not isinstance(swf_event_id, int) or swf_event_id < 0:
          raise ValueError("swf event id should be nonnegative int")
        self.swf_event_id = swf_event_id
        if swf_event_name is None or not isinstance(swf_event_name, unicode) or len(swf_event_name) == 0:
          raise ValueError("swf event name should be nonempty unicode string")
        self.swf_event_name = swf_event_name
        if category is None or not isinstance(category, unicode) or len(category) == 0:
          raise ValueError("event category should be nonempty unicode string")
        self.category = category

        if date_or_date_str is None:
          raise ValueError("event date should not be None")
        elif isinstance(date_or_date_str, date):
          self.date = date_or_date_str
        elif isinstance(date_or_date_str, unicode):
          if len(date_or_date_str) == 0:
            raise ValueError("event date should be passed in as nonempty unicode string")

          try:
              self.date = datetime.strptime(date_or_date_str, "%Y-%b-%d").date()
          except ValueError:
              raise ValueError("event date {} could not be parsed".format(date_or_date_str))
        else:
          raise ValueError("event date was not a string or date")

    def __str__(self):
      return "swf_event_id: {}, swf_event_name: {}, category: {}, date: {}".format(self.swf_event_id, self.swf_event_name, self.category, self.date)

