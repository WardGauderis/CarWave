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


BASE_URL = "http://127.0.0.1:5000/api"
# BASE_URL = "http://team1.ppdb.me/api"

prints = []



# r12 = requests.post(
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
#
# prints.append(request_and_response(r12))
#
# AUTH

r21 = requests.post(
    f"{BASE_URL}/users/auth",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"username": "hayaana", "password": "carwave123"}),
)

prints.append(request_and_response(r21))

# r22 = requests.post(
#     f"{BASE_URL}/users/auth",
#     headers={"Content-Type": "application/json"},
#     data=json.dumps({"username": "tvjkgyphhtfw", "password": "Py88\"B:$"}),
# )
#
# prints.append(request_and_response(r22))
#
# r23 = requests.post(
#     f"{BASE_URL}/users/auth",
#     headers={"Content-Type": "application/json"},
#     data=json.dumps({"username": "qrtdavjtzhwu", "password": "F37ZLv,W"}),
# )
#
# prints.append(request_and_response(r23))
#
# POST RIDE
# TOKEN = r21.json()["token"]
# BEARER_AUTH = f"Bearer {TOKEN}"
#
# r3 = requests.post(
#     f"{BASE_URL}/drives",
#     headers={"Content-Type": "application/json", "Authorization": BEARER_AUTH},
#     data=json.dumps(
#         {
#             "from": [51.130215, 4.571509],
#             "to": [51.18417, 4.41931],
#             "passenger-places": 3,
#             "arrive-by": "2020-05-14T10:00:00.00",
#         }
#     ),
# )

# prints.append(request_and_response(r3))
#
# # GET SPECIFIC RIDE
#
# r4 = requests.get(f"{BASE_URL}/drives/1", headers={"Content-Type": "application/json"})
# prints.append(request_and_response(r4))
#
# # GET PASSENGERS ON A SPECIFIC RIDE
#
# r5 = requests.get(
#     f"{BASE_URL}/drives/1/passengers", headers={"Content-Type": "application/json"}
# )
# prints.append(request_and_response(r5))
#
# r6 = requests.get(
#     f"{BASE_URL}/drives/1/passenger-requests",
#     headers={"Content-Type": "application/json", "Authorization": BEARER_AUTH},
# )
# prints.append(request_and_response(r6))
#
# r7 = requests.get(
#     f"{BASE_URL}/drives/search?limit=7",
#     headers={"Content-Type": "application/json"},
# )
# prints.append(request_and_response(r7))

r8 = requests.get(
    # f"{BASE_URL}/drives/search",
    f"{BASE_URL}/drives/search?to=51.2211097,4.3997081&from=50.879202,4.7011675&arrive_by=2020-05-14T12:00:00.00&sex=male&min_age=20&max_age=25&min_rating=4.0&max_rating=4.7",
    # f"{BASE_URL}/drives/search?from=51.1774729,4.4599307&arrive_by=2020-05-18T10:24:00&to=51.1843856,4.41993868786375",
    # f"{BASE_URL}/drives/search?min_rating=3.5&max_rating=5.6&tags=eh&arrive_by=2020-05-19T21:30:00.00&sex=male",
    # f"{BASE_URL}/drives/search?limit=5&arrive_by=2020-04-23T09:11:00.00",
    # f"{BASE_URL}/drives/search?limit=5&from=51.130215%2C%204.571509&from_distance=1000&to=51.184170%2C%204.419310&to_distance=1000&depart_by=2020-02-12T09%3A30%3A00.00&departure_delta=30&arrive_by=2020-02-12T09%3A30%3A00.00&arrival_delta=30&sex=female&min_consumption=0.5&max_consumption=3.2&min_age=18&max_age=45&min_rating=4.3&max_rating=9.7&tags=friendly%2Cpunctual%2Csafe",
    # f"{BASE_URL}/drives/search?arrive_by=2020-11-14T05:00:00.00&sex=female&min_consumption=1.5&max_consumption=2.3&min_age=26&max_age=44",
    headers={"Content-Type": "application/json"},
)
prints.append(request_and_response(r8))

print(
    "\n\n----------------------------------------------------------------------------------------------------\n\n".join(
        prints))
