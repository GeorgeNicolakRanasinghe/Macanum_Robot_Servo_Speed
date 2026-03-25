#!/usr/local/bin/python3

import json
from datetime import datetime
from websockets.sync.client import connect

token = "c7OieBsRK2QHffpzERauTtsFIXykliPwakjJsxQx5HlJjXiVwWVjaOAGdQG66GZS6Z0RgGquPs2bIyZCBW"
site = "017bcaaf-a074-f5fc-0b1e-083f26226deb"

url = "wss://dash.iiwari.cloud/api/v1/sites/"+site+"/stream?filter=kalman&token="+token

TARGET_NODE = '0d47-3234-0474-80aa'
last_position = None

with connect(url) as websocket:
    while True:
        ev = websocket.recv()
        data = json.loads(ev)
        
        # POSITION UPDATE (type 0)
        if data.get('type') == 0 and data.get('node') == TARGET_NODE:
            x = data['x']
            y = data['y']
            last_position = (x, y)
            print(f"📍 x={x}, y={y}")
        
        # BUTTON PRESS (type 10)
        elif data.get('type') == 10 and data.get('node') == TARGET_NODE:
            if last_position:
                x, y = last_position
                print(f"🔴 BUTTON at x={x}, y={y}")
