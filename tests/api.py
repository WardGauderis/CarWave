# CREATE USER
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# r1 = requests.post(
#     f"{BASE_URL}/users/register",
#     headers={"Content-Type": "application/json"},
#     data=json.dumps(
#         {
#             "username": "MarkP",
#             "firstname": "Mark",
#             "lastname": "Peeters",
#             "password": "MarkIsCool420",
#         }
#     ),
# )

# print(r1)
# print(r1.json())
# print(r1.request.body)

# print("\n\n")

# AUTH

r2 = requests.post(
    f"{BASE_URL}/users/auth",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"username": "MarkP", "password": "MarkIsCool420"}),
)

print(r2)
print(r2.json())
print(r2.request.body)

# POST RIDE

r3 = requests.post(
    f"{BASE_URL}/drives",
    headers={"Content-Type": "application/json", "Authorization": r2.json()["token"]},
    data=json.dumps(
        {
            "from": [51.130215, 4.571509],
            "to": [51.18417, 4.41931],
            "passenger-places": 3,
            "arrive-by": "2020-02-12T10:00:00.00",
        }
    ),
)


# GET SPECIFIC RIDE

r4 = requests.get(f"{BASE_URL}/drives/2", headers={"Content-Type": "application/json"})
