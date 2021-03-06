from threading import Thread
from urllib import request
import json
from time import sleep, localtime, strftime, time
from random import random
from urllib.parse import urlencode
from .config import secret_key
import os
cwd = os.getcwd()

import logging

saved_config = ['autostudy','aim','automove','interval', 'weapon', 'only_best', 'refine_queue_capacity', 'headers', 'tmpl', 'fly_sword', 'transport']

class Account:
    map_data = {}
    def __init__(self, url, user_id, device_id, apns_token='', gdevice_id = None, fversion='1.792', plform='iOS', interval=10, **kwargs):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded;",
            "Origin": "file://",
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92",
            "Accept-Language": "en-us",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }
        self.tmpl = {
              "appId": "com.akmob.xiuzhen",
              "guid": "49-30-23A273",
              "gdeviceId": "869B70F8-D9C5-43E0-9ED8-D2523F7B8E0D",
              "deviceId": "869B70F8-D9C5-43E0-9ED8-D2523F7B8E0D",
              "plform": "iOS",
              "CountryCode": "CN",
              "LanguageCode": "zh",
              "DeviceModelDetail": "iPad8,1",
              "apnsOn": 0,
              "apnsToken": "ef83ffee4a4e8dd53dbcbb6ca732a3ac885380b4d78b72304498a0e0df985e0d",
              "gversion": "1.32",
              "fversion": "1.793",
              "action": "placeholder"
             }
        self.active = True
        self.transport = False
        self.fly_sword = None
        self.weapons = dict()
        self.last_active = time()
        self.url = url
        self.map_data[url] = dict()
        self.user_id = user_id
        self.resource_alert = False
        self.device_id = device_id
        self.tried = 0
        self.only_best = 0
        self.refine_queue_capacity = 1
        self.active_thread = 0
        self.position_notified = False
        try:
            with open('%s/logs/%s.log' % (cwd, user_id), 'r') as logs:
                self.log = "\n\n\n----------- Saved log ------------\n" + logs.read()
        except:
            self.log = ''
        self.print("Server restarted.")
        if gdevice_id:
            self.gdevice_id = gdevice_id
        else:
            self.gdevice_id = device_id
        self.apns_token = apns_token
        self.tmpl['guid'] = user_id
        self.tmpl['gdeviceId'] = self.device_id
        self.tmpl['deviceId'] = self.device_id
        self.tmpl['plform'] = plform
        if 'device' in kwargs:
            self.tmpl["DeviceModelDetail"] = kwargs['device'].replace('_', ',')
        if 'appId' in kwargs and kwargs['appId'] != '':
            self.tmpl['appId'] = kwargs['appId']
            self.appId = kwargs['appId']
        self.interval = int(interval)
        self.status = dict()
        self.aim = None
        self.last_heartbeat = ''
        self.autostudy = False
        self.automove = False
        self.weapon = None
        if 'username' in kwargs:
            self.username = kwargs['username']
        else:
            self.username = 'undefined'
        try:
            self.readConfig()
        except:
            pass
        Thread(target=self.keeper).start()
        Thread(target=self.monitor).start()


    def monitor(self):
        while self.active:
            if (time() - self.last_active) > (self.interval * 3.0):
                    Thread(target=self.keeper).start()
                    self.print("Monitor detect potential timeout occurred. Perform positive restart!")
            sleep(self.interval / 2.0)

    def readConfig(self):
        with open('%s/configs/%s.config' % (cwd, self.user_id), 'r') as config:
            c = json.loads(config.read())
        for i in c:
            self.__setattr__(i, c[i])

    def saveConfig(self):
        c = dict()
        for i in saved_config:
            c[i] = self.__getattribute__(i)
        with open('%s/configs/%s.config' % (cwd, self.user_id), 'w') as config:
            config.write(json.dumps(c))

    def print(self, message):
        l = '\n[%s] %s' % (
                    strftime("%Y-%m-%d %H:%M:%S", localtime()),
                    message
        )
        self.log = l + self.log
        try:
            with open('%s/logs/%s.log' % (cwd, self.user_id), 'a') as logs:
                logs.write(l)
        except:
            pass

    def getLogs(self):
        return (self.last_heartbeat + self.log).replace('\n', '<br/>')

    def getTemplate(self, action, op=''):
        tmp = self.tmpl.copy()
        if "login" in action:
            tmp['action'] = "handler/gameserver/account/LoginGame"
        elif "heart" in action:
            tmp['action'] = "handler/gameserver/account/Heartbeat"
        elif "body" in action:
            tmp['action'] = "handler/gameserver/meridian/ShowMeridians"
        elif "show" in action:
            tmp['action'] = "handler/gameserver/meridian/ShowEvents"
        elif "upgrade" in action:
            tmp['action'] = 'handler/gameserver/meridian/UpgradeMeridian'
            tmp['id'] = op
        elif "event"  in action:
            tmp['action'] = 'handler/gameserver/account/ShowEvents'
        elif "move" in action:
            tmp['action'] = 'handler/gameserver/map/WalkMove'
            tmp['des'] = op
        elif "make" in action:
            tmp['action'] = 'handler/gameserver/weapon/MakeWeapon'
            tmp['count'] = '2'
            tmp['id'] = op
        elif "item" in action:
            tmp['action'] = 'handler/gameserver/item/PlayerWeaponItems'
        elif "destroy" in action:
            tmp['action'] = 'handler/gameserver/weapon/DestroyWeapon'
            tmp['id'] = op
        elif "upweapon" in action:
            tmp['action'] = 'handler/gameserver/weapon/UpgradeWeapon'
            tmp['quality'] = '3'
            tmp['lev'] = '10'
            tmp['id'] = op
        elif "upmagic" in action:
            tmp['action'] = 'handler/gameserver/magic/UpgradeMagic'
            tmp['id'] = op
        elif "speedmagic" in action:
            tmp['action'] = 'handler/gameserver/magic/SpeedupUpgradeMagic'
            tmp['id'] = op
        elif "getmap" in action:
            tmp['action'] = 'handler/gameserver/map/ShowMap'
            tmp['x'] = int(op.split('_')[0])
            tmp['y'] = int(op.split('_')[1])
        elif "singlemap" in action:
            tmp['action'] = 'handler/gameserver/map/ShowSingleMap'
            tmp['coord'] = op
        elif "dailyaward" in action:
            tmp['action'] = 'handler/gameserver/account/GotLoginReward'
        elif "dd" in action:
            tmp['action'] = 'handler/gameserver/quest/CompleteQuest'
            tmp['id'] = "dd00%d" % op
        elif "gottreasure" in action:
            tmp['action'] = 'handler/gameserver/quest/GotTreasure'
            tmp['coord'] = op
            tmp['npc'] = 'npc013'
        elif "getquest" in action:
            tmp['action'] = 'handler/gameserver/quest/ShowQuests'
        elif "finished" in action:
            tmp['action'] = 'handler/gameserver/quest/CompleteQuest'
            tmp['id'] = op
        elif "use" in action:
            tmp['action'] = 'handler/gameserver/item/UseItem'
            tmp['id'] = op
        elif "town" in action:
            tmp['action'] = 'handler/gameserver/map/SignTown'
            tmp['des'] = op
        elif "fly" in action:
            tmp['action'] = 'handler/gameserver/map/FlyMove'
            tmp['des'] = op.split(':')[0]
            tmp['weaponId'] = op.split(':')[1]
        elif "enter" in action:
            tmp['action'] = 'handler/gameserver/quest/SurrenderNpcWin'
            tmp['npc'] = 'm4'
        elif "7day" in action:
            tmp['action'] = 'handler/gameserver/account/Got7DayLoginReward'
        elif "share" in action:
            tmp['action'] = 'handler/gameserver/account/GotShareReward'
        elif "newbie" in action:
            tmp['action'] = 'handler/gameserver/account/NewbieOver'
        return tmp

    def send(self, action, op=''):
        payload = self.getTemplate(action, op)
        req = request.Request(self.url, data=json.dumps(payload).encode(), headers=self.headers)
        # print(json.dumps(payload))
        # print(action)
        re = json.loads(request.urlopen(req).read().decode())
        return re

    def deactive(self):
        self.active = False

    def getQuest(self):
        # try:
            # print(self.send('getquest'))
            return self.send('getquest')['quests']
        # except:
        #     return {}
    def setTarget(self, target):
        try:
            self.print('Set Target to %s' % target)
        except:
            pass
        self.aim = target

    def getMeridians(self):
        re = self.send('body')
        ret = {
            'meridians': [],
            'body': []
        }
        m = re['meridians']
        for k in m:
            if 'meridian' in k:
                ret['meridians'].append({
                    'id': k,
                    'level': m[k]['level']
                })
            elif 'body' in k:
                ret['body'].append({
                    'id': k,
                    'level': m[k]['level']
                })
        return ret

    def upgradeMerdian(self):
        piorities = {
            'body_4': 4,
        }
        d = self.getMeridians()
        m = d['meridians']
        b = d['body']
        min_level = 100
        min_key = ''
        for i in m:
            if i['level'] < min_level:
                min_key = i['id']
                min_level = i['level']
        for i in b:
            if (i['id'] in piorities) and i['level'] < min_level + piorities[i['id']]:
                min_key = i['id']
                min_level = i['level'] - piorities[i['id']]
        self.send('upgrade', min_key)
        self.print('upgrade %s' % min_key)


    def move(self):
        p = self.status['position'].split('_')
        aim = self.aim.split('_')
        p[0] = int(p[0])
        p[1] = int(p[1])
        aim[0] = int(aim[0])
        aim[1] = int(aim[1])
        if not self.transport and self.fly_sword:
            if p[1] == 300:
                self.send('fly', "%d_1:%s" % (p[0], self.fly_sword))
            else:
                self.send('fly', "%d_300:%s" % (p[0], self.fly_sword))
            self.print("Fly~")
            return
        des = self.generate_target()
        if des:
            if not self.transport:
                self.send('move', des)
                self.print("Move to %s" % des)
                return
            else:
                d = des.split('_')
                d[0] = int(d[0])
                d[1] = int(d[1])
                if (p[0] <= d[0] <= aim[0] or p[0] >= d[0] >= aim[0]) and (p[1] <= d[1] <= aim[1] or p[1] >= d[1] >= aim[1]):
                    self.send('move', des)
                    self.print("Move to %s" % des)
                    return
        if p[1] < aim[1]:
            des = "%d_%d" %(p[0], p[1] + 1)
        elif p[1] > aim[1]:
            des = "%d_%d" %(p[0], p[1] - 1)
        elif p[0] < aim[0]:
            des = "%d_%d" % (p[0] + 1, p[1])
        elif p[0] > aim[0]:
            des = "%d_%d" %(p[0] - 1, p[1])
        self.send('move', des)
        self.print("Move to %s" % des)

    def claim(self, position):
        r = self.send("gottreasure", position)
        try:
            self.print('Got Treasuer: %s' % str(r['drop']))
        except:
            pass

    def claim_daily(self):
        quests = self.getQuest()
        unfinished = 4
        for k in quests:
            if 'dd00' in k:
                # print(quests[k])
                if 'finish' not in quests[k]['exts']:
                    unfinished = min(unfinished, int(k[4:]))
            elif k[:2] == 'd0':
                try:
                    if quests[k]['steps'][0]['num'] >= quests[k]['steps'][0]['maxNum']:
                        a.send('finished', k)
                        self.print("Claim %s" % k)
                        return
                except:
                    pass
        if unfinished < 4:
            self.send('dd', unfinished)
            if (unfinished == 1):
                self.send('share')
                self.print("Claim share award")
            self.print('Claim daily award %d' % unfinished)

    def setAutostudy(self, enable=None):
        if enable:
            self.autostudy = enable
        else:
            self.autostudy = not self.autostudy

    def setAutomove(self, enable=None):
        if enable:
            self.automove = enable
        else:
            self.automove = not self.automove

    def setWeapon(self, weapon):
        self.weapon = weapon
        self.print('set weapon to %s' % weapon)

    def gotTreasures(self):
        try:
            b = self.send('getquest')
            self.claim(json.loads(b['quests']['m001']['exts'])['coord'])
        except:
            pass
    
    def generate_target(self):
        try:
            p = self.status['position'].split('_')
            p[0] = int(p[0])
            p[1] = int(p[1])
            if self.map_data[self.url]['%d_%d' % ( p[0] - 1, p[1])] == 'plain':
                return '%d_%d' % ( p[0] - 1, p[1])
            elif self.map_data[self.url]['%d_%d' % ( p[0] + 1, p[1])] == 'plain':
                return '%d_%d' % ( p[0] + 1, p[1])
            elif self.map_data[self.url]['%d_%d' % ( p[0], p[1] - 1)] == 'plain':
                return '%d_%d' % ( p[0], p[1] - 1)
            elif self.map_data[self.url]['%d_%d' % ( p[0], p[1] + 1)] == 'plain':
                return '%d_%d' % ( p[0], p[1] + 1)
        except KeyError:
            if p[0] == 1 or p[0] == 300 or p[1] == 0 or p[1] == 300:
                return False
            try:
                r = self.send('getmap', self.status['position'])['worldMap']['map_list']
                for i in r:
                    self.map_data[self.url][i['gridId']] = i['terrain']
                return self.generate_target()
            except:
                logging.exception("!!")    
        except Exception as e:
            logging.exception("??")
        return False
    
    def refresh_weapons(self):
        wps = self.send('item')['weapons']
        self.weapons = wps

    def notify(self, title, desp = ""):
        req = request.Request("https://sc.ftqq.com/%s.send" % secret_key, data=urlencode({b"text": ("%s - %s" % (title, self.username)).encode('utf-8') , b"desp": desp.encode('utf-8')}).encode('utf-8'))
        request.urlopen(req)
    
    def activeNewbie(self, times=1):
        for _ in range(times):
            self.send('newbie')

    def cleanWeapon(self):
        collects = dict()
        collects2 = dict()
        try:
            wps = self.send('item')['weapons']
            for i in wps:
                sleep(random() * 2)
                if wps[i]['weaponId'] != self.weapon and wps[i]['state'] != 1:
                    continue
                if wps[i]['quality'] < (3 + self.only_best) and wps[i]['level'] == 0:
                    self.send('destroy', i)
                    continue
                if int(wps[i]['level']) >= 8:
                    continue
                if not self.only_best and wps[i]['quality'] == 3:
                    if not collects.__contains__(wps[i]['level']):
                        collects[wps[i]['level']] = i
                    else:
                        self.send('upweapon', i)
                        self.print('Upgrade %s - %s' % (wps[i]['weaponId'], wps[i]['quality']))
                        collects.pop(wps[i]['level'])
                else:
                    if not collects2.__contains__(wps[i]['level']):
                        collects2[wps[i]['level']] = i
                    else:
                        self.send('upweapon', i)
                        self.print('Upgrade %s - %s' % (wps[i]['weaponId'], wps[i]['quality']))
                        collects2.pop(wps[i]['level'])
        except:
            pass

    def keeper(self):
        self.active_thread += 1
        me = self.active_thread
        # self.notify("o0新线程启动0o", "当前线程号为 %d" % me)
        while self.active:
            if me != self.active_thread:
                self.print("Duplicated thread! Thread-%d exited to avoid wasting!" % me)
                return
            self.last_active = time()
            refresh = False
            try:
                re = self.send('heartbeat')
                # print(re)
                self.status['gold'] = re['user']['diamond']
                self.status['siver'] = re['user']['silver']
                self.status['name'] = re['user']['userName']
                self.status['id'] = re['user']['userId']
                self.status['position'] = re['user_other']['XY']
                self.status['pill_count'] = re['user_other']['makePillCount']
                self.status['weapon_count'] = re['user_other']['makeWeaponCount']
                self.status['transport'] = re['user_other']['transportCount']
                self.status['make'] = re['user_other']['makeEventCount']
                self.status['study'] = re['user_other']['studyEventCount']
                self.status['daily_award'] = re['user_other']['dailylogin_get']
                self.status['investIncome'] = re['user_other']['investIncome']
                self.status['pak'] = re['user_other']['pakCapacity']
                self.status['unlock_weapons'] = re['unlock_weapons']
                self.status['resource'] = re['resource_data']['resource']
                self.status['resource_max'] = re['resource_data']['resource_max']
                self.status['dailyquest_ok_count'] = re['dailyquest_ok_count']
                self.status['invest'] = re['user_other'].get("investProfits", {})

                if self.resource_alert:
                    self.resource_alert = False
                    for i in self.status['resource']:
                        if self.status['resource'][i] <= self.status['resource_max'] * 0.05:
                            self.resource_alert = True
                else:
                    for i in self.status['resource']:
                        if self.status['resource'][i] <= self.status['resource_max'] * 0.05:
                            self.resource_alert = True
                            self.notify("o0真气不足0o")
                            break

                re = self.send('event')
                meridian_busy = 0
                move_busy = False
                make_busy = 0
                for i in re['events']:
                    if i.get('exts', False):
                        if 'UpgradeMeridianDone.gv' in i['exts'] or 'UpgradeMagicDone.gv' in i['exts']:
                            meridian_busy += 1
                        elif 'WalkMove' in i['exts'] or ('Fly' in i['exts'] and 'Npc' not in i['exts']):
                            move_busy = True
                        elif 'MakeWeaponDone.gv' in i['exts']:
                            make_busy += 1

                self.status['study'] = meridian_busy
                self.status['make'] = make_busy

                if self.weapon and make_busy < self.refine_queue_capacity:
                    self.send('make', self.weapon)
                    self.print('Make 2x %s' % self.weapon)
                    self.cleanWeapon()
                if self.automove and not move_busy:
                    quests = self.getQuest()
                    if 'm006' in quests:
                        try:
                            if self.aim != json.loads(quests['m006']['exts'])['coord']:
                                self.aim = json.loads(quests['m006']['exts'])['coord']
                                self.print("Detect ongoing transport task. Set it as target!")
                                self.transport = True
                        except:
                            pass
                    elif self.status['position'] == '1_1' and self.aim == '1_1':
                        self.transport = False
                        self.aim = '300_300'
                        self.print('[Automove] Set target as 300_300')
                    elif self.aim == None or (self.status['position'] == '300_300' and self.aim == '300_300'):
                        self.transport = False
                        self.aim = '1_1'
                        self.print('[Automove] Set target as 1_1')
                if not move_busy and self.aim and self.aim != self.status['position']:
                    self.move()
                if self.autostudy and meridian_busy == 0:
                    self.upgradeMerdian()
                if self.aim == self.status['position']:
                    if not self.position_notified:
                        self.notify("o0已到达目的地0o")
                        self.position_notified = True
                else:
                    self.position_notified = False

                if self.status['daily_award']:
                    self.send('dailyaward')
                    self.print('Get login award')

                if self.status['dailyquest_ok_count'] > 0:
                    self.claim_daily()
                self.last_heartbeat = "Last Heartbeat: " + strftime("%Y-%m-%d %H:%M:%S", localtime()) + '<br/><br/>'
                if self.tried > 0:
                    # self.notify("Online Notification")
                    self.print('Login Success!')
                self.tried = 0
                refresh = False
            except:
                try:
                    re = self.send('login')
                    refresh = True
                    self.print('Trying Login...')
                    # self.notify("o00o")                    
                    sleep(3)
                    self.tried += 1
                    if self.tried > 3:
                        self.notify("o0掉线通知0o")
                        self.print('Login Failed! Exited!')
                        self.active = False
                except:
                    pass
            if not refresh:
                sleep(self.interval + random() * 4)
