import sys
import yaml
from scholarly import scholarly

scholar_id = sys.argv[1]

author = scholarly.search_author_id(scholar_id)
author = scholarly.fill(author, sections=['basics', 'indices', 'counts'])

years = author.get('cites_per_year', {})

data = [{"year": int(y), "count": int(c)} for y, c in sorted(years.items(), reverse=True)]

with open("_data/citations.yml", "w") as f:
    yaml.dump(data, f, sort_keys=False)

print("Updated citations.yml")
