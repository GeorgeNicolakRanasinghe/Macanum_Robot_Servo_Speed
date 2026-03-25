#!/usr/local/bin/python3

import json
from websockets.sync.client import connect

token = "c7OieBsRK2QHffpzERauTtsFIXykliPwakjJsxQx5HlJjXiVwWVjaOAGdQG66GZS6Z0RgGquPs2bIyZCBW"
site = "017bcaaf-a074-f5fc-0b1e-083f26226deb"

url = "wss://dash.iiwari.cloud/api/v1/sites/"+site+"/stream?filter=kalman&token="+token

with connect(url) as websocket:
    while True:
        ev = websocket.recv()
        data = json.loads(ev)
        
        # Extract x,y only from type 0 (position) events
        if data.get('type') == 0 and 'x' in data and 'y' in data:
            x = data['x']
            y = data['y']
            ts = data.get('ts', 'no-timestamp')
            node = data.get('node', 'unknown')
            print(f"[{ts}] Node: {node}  x: {x}, y: {y}")
