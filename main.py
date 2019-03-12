from urllib import request
from templates import getTemplates
from multiprocessing import Process
from account import account_keeper
from time import sleep
import json

from config import des, priority, making_weapon

url = "http://xzcngame2.funthree.com:7578/gamen.j"
req_body = request.Request(url, data=json.dumps(getTemplates('body')).encode())
req_body.add_header("Content-Type", "application/json")

req_events = request.Request(url, data=json.dumps(getTemplates('event')).encode())
req_events.add_header("Content-Type", "application/json")

req_item = request.Request(url, data=json.dumps(getTemplates('item')).encode())
req_item.add_header("Content-Type", "application/json")

req_make = request.Request(url, data=json.dumps(getTemplates('make', making_weapon)).encode())
req_make.add_header("Content-Type", "application/json")


if __name__ == "__main__":
    print("Starting up....")
    keeper = Process(target=account_keeper)
    keeper.start()
    # print(request.urlopen(req_body))
    while True:
        min_level = 999
        min_key = "N/A"
        try:
            rep = json.loads(request.urlopen(req_events).read().decode())
            meridian_busy = False
            move_busy = False
            refine_busy = False
            for i in rep['events']:
                if i.get('exts', False):
                    if 'meridian' in i['exts'] or 'magic' in i['exts']:
                        meridian_busy = True
                        pass
                    elif 'WalkMove' in i['exts']:
                        move_busy = True
                    elif 'weapon' in i['exts']:
                        refine_busy = True
            if not meridian_busy:
                rep = json.loads(request.urlopen(req_body).read().decode())
                m = rep['meridians']
                for k in m:
                    if 'meridian' in k:
                        if m[k]['level'] < min_level:
                            min_level = m[k]['level']
                            min_key = k
                if m['body_4']['level'] < (min_level + priority['body_4']): # dan tian
                    min_level = m['body_4']['level'] - priority['body_4']
                    min_key = 'body_4'
                if m['body_1']['level'] < (min_level + priority['body_1']):
                    min_level = m['body_1']['level'] - priority['body_1']
                    min_key = 'body_1'
                if m['body_5']['level'] < (min_level + priority['body_5']):
                    min_level = m['body_5']['level'] - priority['body_5']
                    min_key = 'body_5'
                if "body" in min_key:
                    min_level += priority[min_key]
                req_up = request.Request(url, data=json.dumps(getTemplates('upgrade', min_key)).encode())
                # req_up = request.Request(url, data=json.dumps(getTemplates('upmagic', 'm_sword_3')).encode())
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
            if not refine_busy:
                collects = dict()
                rep = json.loads(request.urlopen(req_item).read().decode())
                for i in rep['weapons']:
                    # print(rep['weapons'][i]['quality'])
                    if rep['weapons'][i]['quality'] < 3:
                        req_destroy = request.Request(url, data=json.dumps(getTemplates('destroy', i)).encode())
                        request.urlopen(req_destroy)
                        # print("Destroy %s/%d" % (rep['weapons'][i]['weaponId'], rep['weapons'][i]['quality']))
                    elif rep['weapons'][i]['weaponId'] == making_weapon:
                        #TODO: Need to be done more precisely
                        # print(rep['weapons'][i]['quality'], rep['weapons'][i]['level'], i)
                        if not collects.__contains__(rep['weapons'][i]['level']):
                            collects[rep['weapons'][i]['level']] = i
                        else:
                            req_upweapon = request.Request(url, data=json.dumps(getTemplates('upweapon', i)).encode())
                            request.urlopen(req_upweapon)
                            print("Upgrade Weapon")
                request.urlopen(req_make)
                print("Make %s" % making_weapon)

            sleep(30)
        except KeyboardInterrupt:
            break
        except:
            pass
    # sleep(20)
