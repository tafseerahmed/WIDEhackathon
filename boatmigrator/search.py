from finna_client import *
from collections import defaultdict

from places import Places

LIMIT = 100

# Search finna.fi for images matching subject
# triples of (id, year, YSO-place location id)
def paged_search(subject, places):
    finna = FinnaClient()
    result = finna.search(subject, search_type=FinnaSearchType.Subject,
                        limit=0, filters=['format:0/Image/', 'online_boolean:1'])

    pages = result['resultCount'] // LIMIT

    filtered = []
    for page in range(pages):
        result = finna.search(subject, search_type=FinnaSearchType.Subject,
            filters=['format:0/Image/', 'online_boolean:1'],
            fields=['id', 'year', 'subjects'],
            sort=FinnaSortMethod.main_date_str_asc,
            limit=LIMIT,
            page=page)
        
        if not 'records' in result:
            print(result)
            break

        for rec in result['records']:
            ident = rec['id']

            if not 'year' in rec:
                continue

            year = int(rec['year'])

            location = ''
            for subject in rec['subjects']:
                s = subject[0]
                if s in places.labels:
                    location = places.labels[s]
                    break

            if location == '':
                continue

            filtered.append((ident, year, location))
    return filtered

# Sort years of images by canonized location
# Returns lat-longs of locations sorted by median year of interest in subject
def vectorized(search, places, min_count=2):
    by_location = defaultdict(list)
    for ident, year, location in search:
        by_location[location].append(year)

    by_canonized_location = defaultdict(list)
    for location, years in by_location.items():
        by_canonized_location[places.canonize(location)] += years

    median_years = []
    for location, years in by_canonized_location.items():
        median = sorted(years)[len(years) // 2]
        median_years.append((location, median))

    points = []
    median_years.sort(key=lambda x: x[1])
    for location, year in median_years:
        if len(by_location[location]) < min_count:
            continue
        points.append(places.to_geo(location))

    return points