import requests

API_URL = "http://localhost:8000/chat"

print("--- Start Chat 1 ---")
# 1. Ask initial question (no conversation_id)
payload1 = {"question": "What is the meaning of John 3:16?", "top_k": 1}
response1 = requests.post(API_URL, json=payload1).json()
conv_id_1 = response1.get("conversation_id")
print("Response 1:", response1.get("answer", "")[:100] + "...")
print("Conversation ID 1:", conv_id_1)

# 2. Ask follow up question (with conversation_id)
payload2 = {"question": "What does 'world' mean in that verse?", "top_k": 1, "conversation_id": conv_id_1}
response2 = requests.post(API_URL, json=payload2).json()
print("Response 2:", response2.get("answer", "")[:100] + "...")
print("Conversation ID from Response 2:", response2.get("conversation_id"))


print("\n--- Start Chat 2 ---")
# 3. Ask new question (no conversation_id)
payload3 = {"question": "What does 'world' mean in that verse?", "top_k": 1}
response3 = requests.post(API_URL, json=payload3).json()
conv_id_2 = response3.get("conversation_id")
print("Response 3:", response3.get("answer", "")[:100] + "...")
print("Conversation ID 2:", conv_id_2)

assert conv_id_1 != conv_id_2, "Isolation failed: Both sessions have the same ID"

print("Done testing!")
