import requests
import random
import time

while True:
    data = {
        "temperature": round(random.uniform(15.0, 30.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2)
    }

    try:
        r = requests.post("http://localhost:8000/api/sensor", json=data)
        print("send: ", data, "|response: ", r.status_code)
    except Exception as e:
        print("Error sending data:", e)

    time.sleep(5)