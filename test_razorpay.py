import os
import requests
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")

print("KEY:", key_id)
print("SECRET FOUND:", bool(key_secret))
print("SECRET LENGTH:", len(key_secret) if key_secret else 0)

url = "https://api.razorpay.com/v1/orders"

data = {
    "amount": 100,
    "currency": "INR",
    "receipt": "test_receipt_001"
}

try:
    print("Sending direct Razorpay request...")

    response = requests.post(
        url,
        auth=(key_id, key_secret),
        json=data,
        timeout=15
    )

    print("STATUS CODE:", response.status_code)
    print("RESPONSE:", response.text)

except Exception as e:
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR:", repr(e))