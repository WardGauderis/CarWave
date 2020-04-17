# CREATE USER
import json
import requests


def str_to_pretty_json(s: str):
    if s is None:
        return "None"
    if isinstance(s, str):
        return json.dumps(json.loads(s), indent=4)
    return json.dumps(dict(s), indent=4)


def request_and_response(r: requests.Request):
    return f"{r.request.url}\n\nRequest\nHeaders:\n{str_to_pretty_json(r.request.headers)}\nBody:\n{str_to_pretty_json(r.request.body)}\n\nResponse\nHeaders:\n{str_to_pretty_json(r.headers)}\nBody:\n{str_to_pretty_json(r.text)}"


BASE_URL = "http://127.0.0.1:5000"

prints = []

r11 = requests.post(
    f"{BASE_URL}/users/register",
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "username": "MarkP",
            "firstname": "Mark",
            "lastname": "Peeters",
            "password": "MarkIsCool420",
        }
    ),
)

prints.append(request_and_response(r11))

r12 = requests.post(
    f"{BASE_URL}/users/register",
    headers={"Content-Type": "application/json"},
    data=json.dumps(
        {
            "username": "MarkP",
            "firstname": "Mark",
            "lastname": "Peeters",
            "password": "MarkIsCool420",
        }
    ),
)

prints.append(request_and_response(r12))

# AUTH

r21 = requests.post(
    f"{BASE_URL}/users/auth",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"username": "MarkP", "password": "MarkIsCool420"}),
)

prints.append(request_and_response(r21))

r22 = requests.post(
    f"{BASE_URL}/users/auth",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"username": "tvjkgyphhtfw", "password": "Py88\"B:$"}),
)

prints.append(request_and_response(r22))

# POST RIDE
TOKEN = r21.json()["token"]
BEARER_AUTH = f"Bearer {TOKEN}"

r3 = requests.post(
    f"{BASE_URL}/drives",
    headers={"Content-Type": "application/json", "Authorization": BEARER_AUTH},
    data=json.dumps(
        {
            "from": [51.130215, 4.571509],
            "to": [51.18417, 4.41931],
            "passenger-places": 3,
            "arrive-by": "2020-02-12T10:00:00.00",
        }
    ),
)

prints.append(request_and_response(r3))

# GET SPECIFIC RIDE

r4 = requests.get(f"{BASE_URL}/drives/1", headers={"Content-Type": "application/json"})
prints.append(request_and_response(r4))

# GET PASSENGERS ON A SPECIFIC RIDE

r5 = requests.get(
    f"{BASE_URL}/drives/1/passengers", headers={"Content-Type": "application/json"}
)
prints.append(request_and_response(r5))

r6 = requests.get(
    f"{BASE_URL}/drives/1/passenger-requests",
    headers={"Content-Type": "application/json", "Authorization": BEARER_AUTH},
)
prints.append(request_and_response(r6))

r7 = requests.get(
    f"{BASE_URL}/drives/search?limit=7",
    headers={"Content-Type": "application/json"},
)
prints.append(request_and_response(r7))

r8 = requests.get(
    f"{BASE_URL}/drives/search",
    headers={"Content-Type": "application/json"},
)
prints.append(request_and_response(r8))

print(
    "\n\n----------------------------------------------------------------------------------------------------\n\n".join(
        prints))
