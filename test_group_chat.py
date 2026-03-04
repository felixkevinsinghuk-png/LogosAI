import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time
import websocket

BASE_URL = "http://localhost:8000"

# 1. Test creation
print("--- Creating Group ---")
response = requests.post(f"{BASE_URL}/group/create", json={"group_name": "Test Group"})
assert response.status_code == 200, "Creation Failed"
room_code = response.json().get("room_code")
print(f"Room Created successfully: {room_code}")
assert len(room_code) == 6, "Room code length is not 6"
assert room_code.isalnum(), "Room code is not alphanumeric"
assert room_code.isupper(), "Room code is not uppercase"

# 2. Test valid validation
print("\n--- Validating Room Code ---")
response = requests.get(f"{BASE_URL}/group/validate/{room_code}")
assert response.status_code == 200, "Validation of valid code failed"
print("Validation passed.")

# 3. Test invalid validation
print("\n--- Validating Invalid Code ---")
response = requests.get(f"{BASE_URL}/group/validate/XXXXXX")
assert response.status_code == 404, "Invalid code did not return 404"
print("Invalid validation rejected correctly.")

# 4. Test WebSocket messaging (Isolation and Sync)
print("\n--- Testing WebSocket Sync ---")
def run_client(name, msg_to_send, expected_msgs):
    ws = websocket.WebSocket()
    ws.connect(f"ws://localhost:8000/ws/group/{room_code}?name={name}")
    
    # Send
    if msg_to_send:
        ws.send(json.dumps({"message": msg_to_send}))
        
    # Receive
    msgs = []
    ws.settimeout(2.0)
    try:
        while len(msgs) < expected_msgs:
            response = ws.recv()
            msgs.append(json.loads(response))
    except websocket.WebSocketTimeoutException:
        pass
        
    ws.close()
    return msgs

# User 1 connects and sends message
res1 = run_client("User1", "Hello from User1", 1)
print(f"User1 received: {res1}")

# User 2 connects (should get history, then can send)
res2 = run_client("User2", "Hello from User2", 2)
print(f"User2 received: {res2}")

print("\n--- All tests passed! ---")
