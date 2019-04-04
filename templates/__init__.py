
templates = {
  "appId": "com.akmob.xiuzhen",
  "guid": "49-30-23A273",
  "gdeviceId": "869B70F8-D9C5-43E0-9ED8-D2523F7B8E0D",
  "deviceId": "869B70F8-D9C5-43E0-9ED8-D2523F7B8E0D",
  "plform": "iOS",
  "CountryCode": "US",
  "LanguageCode": "zh",
  "DeviceModelDetail": "iPad8,1",
  "apnsOn": 0,
  "apnsToken": "ef83ffee4a4e8dd53dbcbb6ca732a3ac885380b4d78b72304498a0e0df985e0d",
  "gversion": "1.32",
  "fversion": "1.792",
  "action": "placeholder"
}

def getTemplates(action, op=""):
    tmp = templates.copy()
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
    return tmp
