import requests

NODE_SERVER_URL = "http://localhost:3000/api/v1/parkings/slot-update"

def send_slot_update(parking_id: str, slot_count: int):
    payload = {
        "parkingId": parking_id,
        "freeSlots": slot_count
    }
    try:
        r = requests.post(NODE_SERVER_URL, json=payload, timeout=2)
        r.raise_for_status()
        print(f"[Notifier] Sent slot update: {slot_count}")
    except requests.RequestException as e:
        print(f"[Notifier ERROR] Failed to send slot update: {e}")
