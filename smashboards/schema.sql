-- Users on SWF
CREATE TABLE `players` (
  `id` int(11) NOT NULL PRIMARY KEY,
  `username` varchar(63) NOT NULL,
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB CHARACTER SET=utf8;

-- Tags used in tournaments on SWF
CREATE TABLE `tags` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `tag` varchar(255) NOT NULL,
  UNIQUE KEY `tag` (`tag`)
) ENGINE=InnoDB CHARACTER SET=utf8;

-- Mapping between players and tags
CREATE TABLE `player_tag_map` (
  `id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `player_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  CONSTRAINT `player_tag_map_ibfk1`
    FOREIGN KEY(`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `player_tag_map_ibfk2`
    FOREIGN KEY(`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE `characters` (
  `player_id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
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
  KEY `character_name` (`character_name`)
) ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE `events` (
  `id` int(11) NOT NULL PRIMARY KEY,
  `event_name` varchar(255) NOT NULL,
  `category` ENUM(
    'Premier', 'Global', 'International',
    'National', 'Regional', 'Local',
    'Large Local', 'Pools', 'Teams') NOT NULL,
  `event_date` DATE NOT NULL,
  KEY `event_name` (`event_name`),
  KEY `category` (`category`),
  KEY `event_date` (`event_date`)
) ENGINE=InnoDB CHARACTER SET=utf8;

CREATE TABLE `event_to_player_tag_map` (
  `player_tag_map_id` INT(11) NOT NULL,
  `event_id` INT(11) NOT NULL,
  CONSTRAINT `event_to_player_tag_map_ibfk1`
    FOREIGN KEY(`player_tag_map_id`) REFERENCES `player_tag_map` (`id`) ON DELETE CASCADE,
  CONSTRAINT `event_to_player_tag_map_ibfk2`
    FOREIGN KEY(`event_id`) REFERENCES `events` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB CHARACTER SET=utf8;

