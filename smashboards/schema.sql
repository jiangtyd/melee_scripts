-- Users on SWF
CREATE TABLE `players` (
  `id` int(11) NOT NULL PRIMARY KEY,
  `username` varchar(63) NOT NULL,
  KEY `username` (`username`)
) ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE `characters` (
  `player_id` int(11) NOT NULL,
  `character_name` ENUM(
    'fox', 'falco', 'marth', 'sheik',
    'falcon', 'peach', 'jigglypuff', 'ic',
    'samus', 'ganon', 'luigi', 'drmario',
    'link', 'pikachu', 'yoshi', 'dk',
    'roy', 'mario', 'zelda', 'gamewatch',
    'ylink', 'kirby', 'ness', 'bowser',
    'mewtwo', 'pichu') NOT NULL,
  CONSTRAINT `characters_ibfk1`
    FOREIGN KEY(`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  KEY `character_name` (`character_name`),
  UNIQUE KEY `characters_player` (`player_id`, `character_name`)
) ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE `events` (
  `id` int(11) NOT NULL PRIMARY KEY,
  `event_name` varchar(255) NOT NULL,
  `category` ENUM(
    'Premier', 'Global', 'International',
    'National', 'Regional', 'Local',
    'Large Local', 'Pools', 'Teams',
    'Unranked', 'Online') NOT NULL,
  `event_date` date NOT NULL,
  `host` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `uploader_id` int(11) NOT NULL,
  KEY `event_name` (`event_name`),
  KEY `event_category` (`category`),
  KEY `event_date` (`event_date`),
  KEY `event_host` (`host`),
  KEY `event_location` (`location`),
  CONSTRAINT `events_ibfk1`
    FOREIGN KEY(`uploader_id`) REFERENCES `players` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB CHARACTER SET=utf8;

-- Mapping between players, tags used in SWF tournaments, and the event the tag was used at
CREATE TABLE `player_tag_map` (
  `player_id` int(11) NOT NULL,
  `tag` varchar(255) NOT NULL,
  `event_id` int(11) NOT NULL,
  CONSTRAINT `player_tag_map_ibfk1`
    FOREIGN KEY(`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `player_tag_map_ibfk2`
    FOREIGN KEY(`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE,
  KEY `tag` (`tag`),
  UNIQUE KEY `player_tag_map_event` (`player_id`, `event_id`)
) ENGINE=InnoDB CHARACTER SET=utf8;

-- "Scoring" of possible tags a player might use ("related to the player").
-- Computed from `player_tag_map` (see db.py), but we precompute it for lookup efficiency
CREATE TABLE `player_related_tags` (
  `player_id` int(11) NOT NULL,
  `related_tag` varchar(255) NOT NULL,
  `score` int(11) NOT NULL,
  CONSTRAINT `player_related_tags_ibfk1`
    FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  KEY `related_tag` (`related_tag`),
  UNIQUE KEY `player_related_tag` (`player_id`, `related_tag`)
) ENGINE=InnoDB CHARACTER SET=utf8;

