import hashlib, hmac, json, time, urllib.request

WEBHOOK_SECRET = "placeholder"
PAYMENT_INTENT_ID = "pi_3U9Rv9I0MgiiqR1Q1saSEAR4"

payload = json.dumps({
    "id": "evt_manual_test",
    "type": "payment_intent.succeeded",
    "data": {"object": {"id": PAYMENT_INTENT_ID, "amount": 2000}}
}).encode()
timestamp = str(int(time.time()))
signed_payload = f"{timestamp}.{payload.decode()}"
signature = hmac.new(WEBHOOK_SECRET.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
sig_header = f"t={timestamp},v1={signature}"
req = urllib.request.Request(
    "http://127.0.0.1:8000/webhooks/stripe",
    data=payload,
    headers={"stripe-signature": sig_header, "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req) as response:
        print(response.status, response.read().decode())
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())