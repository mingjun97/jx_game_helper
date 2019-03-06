from urllib import request, parse
import json
from templates import getTemplates
from time import sleep

def account_keeper():
    print("Account Keeper Starting Up...")

    url = "http://xzcngame2.funthree.com:7578/gamen.j"

    req = request.Request(url, data = json.dumps(getTemplates('heartbeat')).encode())
    req.add_header("Content-Type", 'application/json')

    login_request = request.Request(url, data = json.dumps(getTemplates('login')).encode())
    login_request.add_header("Content-Type", 'application/json')

    while True:
        # print("Heartbeat..")
        rep = json.loads(request.urlopen(req).read().decode())
        if rep['code'] != 0:
            request.urlopen(login_request)
            print("Heartbeat timeout, trying login..")
        sleep(5)
