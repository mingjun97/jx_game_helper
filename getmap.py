from templates import getTemplates
from urllib import request
import json


url = "http://xzcngame2.funthree.com:7578/gamen.j"
for i in range(4, 300, 7):
    for j in range(5, 300, 9):
        coord = "%d_%d" % (i, j)
        getmap = request.Request(url,  data=json.dumps(getTemplates('getmap',coord)).encode())
        # print(request.urlopen(getmap).read().decode())
        rep = json.loads(request.urlopen(getmap).read().decode())
        for k in rep['worldMap']['walker_counts']:
            getsinglemap = request.Request(url,  data=json.dumps(getTemplates('singlemap',k)).encode())
            rep_single = json.loads(request.urlopen(getsinglemap).read().decode())
            # print(rep_single)
            for r in rep_single['map_grid']['walkers']:
                # print(r)
                print("%s, %s, %s, %s" % (r['gridId'], r['walkerId'], r['walkerName'], r['exts']))
