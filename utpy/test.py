import urllib3
import re
import json
from main import load

# re= ytInitialData\s*=\s*({.+?})\s*;\s*(?:var\s+meta|<\/script|\n)

url = 'https://www.youtube.com/watch?v=NH4VZaP3_9s&list=PLOLrQ9Pn6cay_BE9pz1djcqW0-p2QiRUx&index=2'

# http = urllib3.PoolManager()

# response = http.request('GET', url)

# data = response.data.decode('utf-8')

# ytinitdata = re.findall('ytInitialData\s*=\s*({.+?})\s*;\s*(?:var\s+meta|<\/script|\n)', data)
# info_json = json.loads(ytinitdata[0])

# print(info_json['microformat']['microformatDataRenderer']['urlCanonical'])
yt= load(url)

print(yt.data())