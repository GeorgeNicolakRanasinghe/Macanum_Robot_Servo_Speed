#!/usr/local/bin/python3

import json
from websockets.sync.client import connect

token = "c7OieBsRK2QHffpzERauTtsFIXykliPwakjJsxQx5HlJjXiVwWVjaOAGdQG66GZS6Z0RgGquPs2bIyZCBW"
site = "017bcaaf-a074-f5fc-0b1e-083f26226deb"

url = "wss://dash.iiwari.cloud/api/v1/sites/"+site+"/stream?filter=kalman&token="+token

# Your two tags
USER_TAG = '0d47-3234-0474-80aa'  # Main tag (z=100)
ROBOT_TAG = '1347-3932-1592-420a'  # Second tag (z=0)

last_pos_USER_TAG = None
last_pos_ROBOT_TAG = None

with connect(url) as websocket:
    while True:
        ev = websocket.recv()
        data = json.loads(ev)
        
        node = data.get('node')
        
        # TAG 1: 0d47-3234-0474-80aa (z=100)
        if data.get('type') == 0 and node == USER_TAG:
            x = data['x']
            y = data['y']
            last_pos_USER_TAG = (x, y)
            print(f"📍 USER_TAG: x={x}, y={y}")
        
        elif data.get('type') == 10 and node == USER_TAG:
            if last_pos_USER_TAG:
                x, y = last_pos_USER_TAG
                print(f"🔴 USER_TAG BUTTON at x={x}, y={y}")
        
        # TAG 2: 1347-3932-1592-420a (z=0)  
        elif data.get('type') == 0 and node == ROBOT_TAG:
            x = data['x']
            y = data['y']
            last_pos_ROBOT_TAG = (x, y)
            print(f"📍 ROBOT_TAG: x={x}, y={y}")
        
        elif data.get('type') == 10 and node == ROBOT_TAG:
            if last_pos_ROBOT_TAG:
                x, y = last_pos_ROBOT_TAG
                print(f"🔴 ROBOT_TAG BUTTON at x={x}, y={y}")
