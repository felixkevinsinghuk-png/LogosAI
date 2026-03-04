import requests
import json
import websocket
from concurrent.futures import ThreadPoolExecutor
import time

BASE_URL = "http://localhost:8000"

print("--- Creating Group ---")
response = requests.post(f"{BASE_URL}/group/create", json={"group_name": "Test Group Limit"})
assert response.status_code == 200, "Creation Failed"
room_code = response.json().get("room_code")
print(f"Room Created successfully: {room_code}")

print("\n--- Connecting 13 Clients ---")
clients = []
def connect_client(i):
    ws = websocket.WebSocket()
    url = f"ws://localhost:8000/ws/group/{room_code}?name=User{i}"
    try:
        ws.connect(url)
        return ws
    except Exception as e:
        print(f"Failed to connect User{i}: {e}")
        return None

results = []
for i in range(1, 14):
    results.append(connect_client(i))
    time.sleep(0.05)
    
for res in results:
    if res:
        clients.append(res)
        
print(f"Successfully connected {len(clients)} clients.")
assert len(clients) == 13

print("\n--- Verifying Capacity Limit (Attempting 14th) ---")
ws_14 = websocket.WebSocket()
success = False
try:
    ws_14.connect(f"ws://localhost:8000/ws/group/{room_code}?name=User14")
    response = ws_14.recv()
    if response == "" or response is None:
        print("14th connection closed by server immediately (expected).")
        success = True
    else:
        print(f"WARNING: 14th user connected successfully, limit failed! Received: {response}")
except websocket.WebSocketBadStatusException as e:
    print(f"Handshake rejected. This is acceptable. {e}")
    success = True
except websocket.WebSocketConnectionClosedException as e:
    print("Connection closed correctly on 14th user.")
    success = True
except Exception as e:
    print(f"14th Client connect failed as expected: {e}")
    success = True

val_res = requests.get(f"{BASE_URL}/group/validate/{room_code}").json()
print("Validation Info after 14th:", val_res)
assert val_res['full'] == True, "Validation did not report full room"
assert val_res['info']['participants'] == 13, "Participants count is wrong"

print("\n--- Disconnecting ONE client ---")
clients[0].close()
time.sleep(1)

print("\n--- Testing HTTP Validation After Disconnect ---")
val_res2 = requests.get(f"{BASE_URL}/group/validate/{room_code}").json()
print("Validation Info:", val_res2)
assert val_res2['full'] == False, "Validation still reported full room after disconnect"
assert val_res2['info']['participants'] == 12, "Participants count is wrong"

print("\n--- All tests passed! Server strictly enforces limits! ---")
for c in clients[1:]:
    c.close()
