
templates = {
  "fversion" : "1.792",
  "apnsToken" : "addabc6459dc9208c32981749e9361a20a5fbc9f5c99413db66b093986720805",
  "CountryCode" : "CN",
  "DeviceModelDetail" : "iPhone10,3",
  "appId" : "xxipa.4.497YH95P2T.89913700408b9b67f27b74f7278a13f3",
  "deviceId" : "CF5AB40C-59F8-4E78-97FE-5A76923DC949",
  "action" : "handler\/gameserver\/account\/Heartbeat",
  "gdeviceId" : "774D2778-8C05-4E58-928B-0A5A1991221B",
  "LanguageCode" : "zh",
  "guid" : "49-69-10A140",
  "plform" : "iOS",
  "gversion" : "1.32",
  "apnsOn" : 1
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
