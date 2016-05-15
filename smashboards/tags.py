import re

# useful regexes
any_sep = re.compile('[\|\.`]')
space_sep_sponsors = re.compile('([A-Z0-9]+ )+(.+)')

def rm_spaces(tag):
  return tag.replace(' ', '')

def rm_separated_sponsors(tag):
  split_tag = any_sep.split(tag)
  if len(split_tag) > 1: # tag contains sep; assume last part is "base tag"
    return split_tag[-1].strip()
  else:
    return None

def rm_space_separated_sponsors(tag):
  # if tag looks like P4K MVG Mew2king
  space_sep_matches = PlayerRepository.space_sep_sponsors.match(tag)
  if space_sep_matches:
    return space_sep_matches.group(2)
  else:
    return None

def compute_scores(tag):
  ''' some tags might be None; take care in caller '''
  return [
      (rm_space_separated_sponsors(tag), 5),
      (rm_separated_sponsors(tag), 7),
      (rm_spaces(tag), 8)
      (tag, 10)
  ]

def sorted_asc_score(lst):
  return sorted(lst, key=lambda x: x[1])

def sorted_desc_score(lst):
  return sorted(lst, key=lambda x: -x[1])

def compute_related_tags(original_tag):
  tag = original_tag.lower() # use lowercase as canonical version
  related_tags = {}
  
  # assign scores to potential related tags
  # pretty arbitrary for now
  # overwrite lower scores with higher
  for related_tag, score in sorted_asc_score(compute_scores(tag)):
    if related_tag:
      related_tags[related_tag] = score

  return related_tags

def generate_similar_tags_regexps(self, tag):
  # regexes to check
  # exact matches
  exact = [('^' + related + '$', score + 10) for related, score in compute_scores(tag)]
  # match with a prefix
  with_prefixes = [('.*[\|\.` ]' + related + '$', score) for related, score in compute_scores(tag)]
  return (sorted_desc_score(exact), sorted_desc_score(with_prefixes))

