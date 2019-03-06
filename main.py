from urllib import request
from templates import getTemplates
from multiprocessing import Process
from account import account_keeper
from time import sleep
import json


url = "http://xzcngame2.funthree.com:7578/gamen.j"
req_body = request.Request(url, data=json.dumps(getTemplates('body')).encode())
req_body.add_header("Content-Type", "application/json")

req_events = request.Request(url, data=json.dumps(getTemplates('event')).encode())
req_events.add_header("Content-Type", "application/json")

des = [208,254]

if __name__ == "__main__":
    print("Starting up....")
    keeper = Process(target=account_keeper)
    keeper.start()
    # print(request.urlopen(req_body))
    while True:
        try:
            rep = json.loads(request.urlopen(req_events).read().decode())
            meridian_busy = False
            move_busy = False
            for i in rep['events']:
                # print(i)
                if i.get('exts', False):
                    if 'meridian' in i['exts']:
                        meridian_busy = True
                    elif 'WalkMove' in i['exts']:
                        move_busy = True
                        # print(i['exts'])
            if not meridian_busy:
                rep = json.loads(request.urlopen(req_body).read().decode())
                min_level = 10
                min_key = "merdian"
                m = rep['meridians']
                for k in m:
                    if 'meridian' in k:
                        if m[k]['level'] < min_level:
                            min_level = m[k]['level']
                            min_key = k
                    if 'body_4' in k: # Dantian
                        if m[k]['level'] < min_level + 6:
                            min_level = m[k]['level']
                            min_key = k
                    if 'body_1' in k: # Xiuli
                        if m[k]['level'] < min_level + 6:
                            min_level = m[k]['level']
                            min_key = k
                    if 'body_1' in k: # Lianti
                        if m[k]['level'] < min_level + 2:
                            min_level = m[k]['level']
                            min_key = k
                req_up = request.Request(url, data=json.dumps(getTemplates('upgrade',min_key)).encode())
                resp = request.urlopen(req_up).read().decode()
                print('upgrade: %s from %d -> %d' % (min_key, min_level, min_level+1))
            if not move_busy:
                rep = json.loads(request.urlopen(req_body).read().decode())
                p = rep['user_other']['XY'].split('_')
                p[0] = int(p[0])
                p[1] = int(p[1])
                payload = getTemplates('move')
                if p[1] < des[1]:
                    payload['des'] = "%d_%d" %(p[0], p[1] + 1)
                elif p[1] > des[1]:
                    payload['des'] = "%d_%d" %(p[0], p[1] - 1)
                elif p[0] < des[0]:
                    payload['des'] = "%d_%d" % (p[0] + 1, p[1])
                elif p[0] > des[0]:
                    payload['des'] = "%d_%d" %(p[0] - 1, p[1])
                else:
                    continue
                req_move = request.Request(url, data=json.dumps(payload).encode())
                resp = request.urlopen(req_move).read().decode()
                print("move: from %d_%d to %s" %(p[0], p[1], payload['des']))
            sleep(30)
        except KeyboardInterrupt:
            break
        except:
            pass
    # sleep(20)
