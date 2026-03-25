#!/usr/local/bin/python3

import json
from websockets.sync.client import connect

token = "c7OieBsRK2QHffpzERauTtsFIXykliPwakjJsxQx5HlJjXiVwWVjaOAGdQG66GZS6Z0RgGquPs2bIyZCBW" # your personal token
site = "017bcaaf-a074-f5fc-0b1e-083f26226deb" # your site's ID

url = "wss://dash.iiwari.cloud/api/v1/sites/"+site+"/stream?filter=kalman&token="+token

with connect(url) as websocket:
    while True:
        ev = websocket.recv()
        print(json.loads(ev))


