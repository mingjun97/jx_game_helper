from urllib import request
from urllib.parse import urlencode
import json


from .tmpl import header_template, packet_template

actions = {
    'login': {'action': lambda _,__ :"handler/gameserver/account/LoginGame"},
    'heartBeat': {'action': lambda _,__ :"handler/gameserver/account/Heartbeat"},
    'getLoginAward': {'action': lambda _,__: "handler/gameserver/account/GotLoginReward"},
    '7dayLoginAward': {'action': lambda _,__: "handler/gameserver/account/Got7DayLoginReward"},
    'getShareAward': {'action': lambda _,__: "handler/gameserver/account/GotShareReward"},

    'complete': {'action': lambda _,__: "handler/gameserver/quest/CompleteQuest", 'id': lambda x,_: x},
    'gotTreasure': {'action': lambda _,__: "handler/gameserver/quest/GotTreasure", 'coord': lambda x,_: x, 'npc': lambda _,__: 'npc013'},
    'showQuest': {'action': lambda _,__: "handler/gameserver/quest/ShowQuests"},
    'enterCave': {'action': lambda _,__: "handler/gameserver/quest/SurrenderNpcWin", 'npc': lambda x,__: 'm4' if not x else 'm3'},


    'showMeridian': {'action': lambda _,__ :"handler/gameserver/meridian/ShowMeridians"},
    'upgradeMeridian': {'action': lambda _,__ :"handler/gameserver/meridian/UpgradeMeridian", 'id': lambda x,_: x},
    
    'upgradeMagic': {'action': lambda _,__ :"handler/gameserver/magic/UpgradeMagic", 'id': lambda x,_: x},    
    'speedupMagic': {'action': lambda _,__ :"handler/gameserver/magic/SpeedupUpgradeMagic", 'id': lambda x,_: x},
    
    'event': {'action': lambda _,__ : "handler/gameserver/account/ShowEvents"},

    'walk': {'action': lambda _,__ :"handler/gameserver/map/WalkMove", 'des': lambda x,_: x},
    'fly': {'action': lambda _,__ :"handler/gameserver/map/FlyMove", 'des': lambda x,_: x, 'weaponId': lambda _,x: x},
    'signTown': {'action': lambda _,__ :"handler/gameserver/map/SignTown", 'des': lambda x,_: x},
    'getMap': {'action': lambda _,__ :"handler/gameserver/map/ShowMap", 'x': lambda x,_: x, 'y': lambda _,x: x},
    'showMap': {'action': lambda _,__ :"handler/gameserver/map/ShowSingleMap", 'coord': lambda x,y: "%d_%d" %(x,y)},

    'make': {'action': lambda _,__ :"handler/gameserver/weapon/MakeWeapon", 'id': lambda x,_: x, 'count': lambda _,x: x if x else 2},
    'use': {'action': lambda _,__ :"handler/gameserver/item/UseItem", 'id': lambda x,_: x},
    'item': {'action': lambda _,__ :"handler/gameserver/item/PlayerWeaponItems"},
    'destroy': {'action': lambda _,__ :"handler/gameserver/weapon/DestroyWeapon", 'id': lambda x,_: x},
    'upgradeWeapon': {'action': lambda _,__ :"handler/gameserver/item/UpgradeWeapon", 'id': lambda x,_: x, 'quality': lambda _,x: int(x.split(':')[0]) if x else 3, 'lev': lambda _,x: int(x.split(':')[1]) if x else 10},
}

class Character:
    def __init__(self, url, user_id, device_id='', apns_token='', gdevice_id = None, plform='iOS', **kwargs):
        self.headers = header_template.copy()
        self.packet = packet_template.copy()
        self.url = url
        self.packet['guid'] = user_id
        self.packet['gdeviceId'] = gdevice_id if gdevice_id else device_id
        self.packet['deviceId'] = device_id
        self.packet['plform'] = plform
        if 'device' in kwargs:
            self.packet["DeviceModelDetail"] = kwargs['device'].replace('_', ',')
        if 'appId' in kwargs and kwargs['appId'] != '':
            self.packet['appId'] = kwargs['appId']
            self.appId = kwargs['appId']
        self.status = dict()
        self.items = []
        self.weapons = dict()

    def send(self, action, op1=None, op2=None):
        if action not in actions:
            raise IndexError()
        tmp = self.packet.copy()
        for k in actions[action]:
            tmp[k] = actions[action][k](op1, op2)
        req = request.Request(self.url, data=json.dumps(tmp).encode(), headers=self.headers)
        re = json.loads(request.urlopen(req).read().decode())
        if 'fileVersion' in re:
            self.packet['fversion'] = re['fileVersion']
            return self.send(action, op1, op2)
        return re

    def update(self, retry=False):
        try:
            re = self.send('heartBeat')
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
        
            re = self.send('event')
            study_busy = 0
            move_busy = False
            make_busy = 0
            for i in re['events']:
                if i.get('exts', False):
                    if 'UpgradeMeridianDone.gv' in i['exts'] or 'UpgradeMagicDone.gv' in i['exts']:
                        study_busy += 1
                    elif 'WalkMove' in i['exts'] or ('Fly' in i['exts'] and 'Npc' not in i['exts']):
                        move_busy = True
                    elif 'MakeWeaponDone.gv' in i['exts']:
                        make_busy += 1

            self.status['study'] = study_busy
            self.status['make'] = make_busy

        except:
            self.send('login')
            if retry:
                self.update()
            raise KeyError()
    
    def getMeridians(self):
        re = self.send('showMeridian')
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

    @staticmethod
    def getActions():
        return {'actions': list(actions.keys()) }
    
    @staticmethod
    def getNumberOfActionOps(action):
        try:
            return {'count': len(actions[action].keys()) - 1}
        except:
            return {'count': -1}