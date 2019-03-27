from threading import Thread
from urllib import request
import json
from time import sleep

class Account:
    tmpl = {
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
      "fversion": "1.792",
      "action": "placeholder"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;",
        "Origin": "file://",
        "User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16B92",
        "Accept-Language": "en-us",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
    }
    def __init__(self, url, user_id, device_id, apns_token, fversion='1.792', plform='iOS', interval=10):
        self.active = True
        self.url = url
        self.user_id = user_id
        self.device_id = device_id
        self.apns_token = apns_token
        self.tmpl['guid'] = user_id
        self.tmpl['gdeviceId'] = self.device_id
        self.tmpl['deviceId'] = self.device_id
        self.tmpl['plform'] = plform
        self.interval = interval
        self.status = dict()
        Thread(target=self.keeper).start()

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
            tmp['count'] = '1'
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

    def keeper(self):
        while self.active:
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
            except:
                try:
                    re = self.send('login')
                    # print(re)
                except:
                    pass
            sleep(self.interval)
