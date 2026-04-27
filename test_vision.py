import requests
import uuid
import time

# Target the Dockerized server port
BASE_URL = "http://localhost:8011/api/chat"
# Unique ID for this test run
CONV_ID = f"test_{uuid.uuid4().hex[:8]}"

def send_message(message):
    """Utility to send a message and print the conversation."""
    print(f"\n[Guest]: {message}")
    try:
        response = requests.post(
            f"{BASE_URL}/{CONV_ID}/message",
            json={"content": message},
            timeout=30
        )
        if response.status_code == 200:
            reply = response.json()["content"]
            print(f"[Agent]: {reply}")
            return reply
        else:
            print(f"FAILED: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        return None

def run_vision_test():
    print("="*60)
    print(f"STAYEASE AI AGENT - VISION TEST (CONV: {CONV_ID})")
    print("="*60)
    
    print("\nSTAGE 1: SEARCHING")
    print("-" * 20)
    send_message("Hi! I'm looking for a place to stay in Cox's Bazar for 2 people.")
    
    time.sleep(1)
    print("\nSTAGE 2: DETAILS")
    print("-" * 20)
    send_message("That Sea View Suite sounds nice. What are the details?")
    
    time.sleep(1)
    print("\nSTAGE 3: BOOKING")
    print("-" * 20)
    send_message("Great! Please book it for me. Name is John Doe, dates 2026-06-01 to 2026-06-03.")
    
    time.sleep(1)
    print("\nSTAGE 4: ESCALATION (Out of Scope)")
    print("-" * 20)
    send_message("Thanks! Also, can you recommend a good flight from Dhaka to London?")
    
    print("\n" + "="*60)
    print("VISION TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_vision_test()

