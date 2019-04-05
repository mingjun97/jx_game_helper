from templates import getTemplates
from urllib import request
import json
from time import sleep
from threading import Thread

headers = {
    "Content-Type": "application/x-www-form-urlencoded;",
    "Origin": "file://",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
}

url = "http://xzcngame1.funthree.com:7578/gamen.j"

def keeper():
    login = request.Request(url,  data=json.dumps(getTemplates('login')).encode(), headers=headers)
    request.urlopen(login)
    hb = request.Request(url,  data=json.dumps(getTemplates('heartbeat')).encode(), headers=headers)
    while True:
        request.urlopen(hb)
        sleep(5)

Thread(target=keeper).start()

sleep(1)
count = 0

def watch(i):
    global count
    for j in range(5, 300, 9):
        coord = "%d_%d" % (i, j)
        getmap = request.Request(url,  data=json.dumps(getTemplates('getmap',coord)).encode(), headers=headers)
        # print(request.urlopen(getmap).read().decode())
        try:
            rep = json.loads(request.urlopen(getmap).read().decode())
        except:
            sleep(3)
            try:
                rep = json.loads(request.urlopen(getmap).read().decode())
            except:
                sleep(3)
                rep = json.loads(request.urlopen(getmap).read().decode())
        # print(rep)
        for k in rep['worldMap']['walker_counts']:
            getsinglemap = request.Request(url,  data=json.dumps(getTemplates('singlemap',k)).encode(), headers=headers)
            rep_single = json.loads(request.urlopen(getsinglemap).read().decode())
            # print(rep_single)
            for r in rep_single['map_grid']['walkers']:
                # print(r)
                print("%s, %s, %s, %s" % (r['gridId'], r['walkerId'], r['walkerName'], r['exts']))
    count -= 1

for i in range(4, 300, 7):
    while count > 1 :
        sleep(1)
    count += 1
    Thread(target=watch, args=(i,)).start()
