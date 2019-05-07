from flask import Flask, redirect
import flask_login
from helper import Account

accounts = dict()
rank_list = list()

app = Flask(__name__)

lookuptable = {
    'username': 0,
    'user_id': 1,
    'device_id': 3,
    'gdevice_id': 2,
    'interval': 4,
    'url': 5,
    'device': 6,
    'appId': 7
}

redirect_message = "<br/> Redirect in 2 seconds. <script> setTimeout(function(){window.history.back()}, 2000)</script>"
def lookup(d, k):
    return d[lookuptable[k]]

with open('account.csv') as b:
    a = b.read().replace('\ufeff', '')
for i in a.split('\n'):
    if len(i) > 5:
        record = i.split(',')
        cur = lookup(record, 'user_id')
        rank_list.append(cur)
        tmp = dict()
        for k in lookuptable:
            tmp[k] = lookup(record, k)
        # print(tmp)
        accounts[cur] = Account(**tmp)

@app.route('/user/autostudy/<string:id>')
def setAutostudy(id):
    accounts[id].setAutostudy()
    return redirect('/user/%s' % id)

@app.route('/user/automove/<string:id>')
def setAutomove(id):
    accounts[id].setAutomove()
    return redirect('/user/%s' % id)

@app.route('/user/<string:id>/save')
def save(id):
    accounts[id].saveConfig()
    return redirect('/user/%s' % id)

@app.route('/user/<string:id>/load')
def load(id):
    accounts[id].readConfig()
    return redirect('/user/%s' % id)

@app.route('/user/<string:id>')
def user(id):
    result = '<h1>%s</h1>' % accounts[id].username
    result += 'Save Config: <a href="/user/%s/save"> Save </a><br/>' % id

    if not accounts[id].active:
        result += '<a href="/restart/%s" style="color: red"> Restart This User </a><br/><br/>' % id
    result += 'Auto Study: <a href="/user/autostudy/%s">' % id + \
        ('On' if accounts[id].autostudy else 'Off') + \
    '</a><br/>'


    result += 'Auto Move: <a href="/user/automove/%s">' % id + \
        ('On' if accounts[id].automove else 'Off') + \
    '</a><br/>'
    result += "<br/>"

    result += 'Set Interval: <a href="/set-interval/%s/N"> Go' % id + \
    '</a><br/>'
    result += "<br/>"

    result += 'Got treasure: <a href="/treasure/%s/N">' % id + \
        'Go' + \
    '</a><br/>'
    result += "<br/>"

    result += 'Target: <a href="/target/%s/N">%s</a> <br/>' % (id,accounts[id].aim)
    result += "<br/>"

    if 'unlock_weapons' in accounts[id].status:
        result += 'Set automake weapon(%d)' % accounts[id].refine_queue_capacity
        if accounts[id].weapon:
            result += '[<a href="/set-weapon/%s/Unset">%s</a>]' % (id, accounts[id].weapon)
        result += " : "
        for i in accounts[id].status['unlock_weapons']:
            result += '<a href="/set-weapon/%s/%s">%s</a>&nbsp;&nbsp;' % (id, i, i)
        result += '&nbsp;&nbsp;&nbsp;&nbsp; <a href="/only-best/%s" style="color: red"> only best!</a>' % id
        result += '</br></br>'
        result += 'Refine capacity: <a href="/up-weapon-capacity/%s">+1</a>' \
                  '&nbsp;&nbsp;<a href="/down-weapon-capacity/%s">-1</a>' % (id, id)
    result += '</br></br>' + str(accounts[id].status)
    result += "<br/><br/>"
    result += accounts[id].getLogs()
    return result

@app.route('/only-best/<string:id>')
def onlyBest(id):
    accounts[id].only_best = 1

@app.route('/set-weapon/<string:id>/<string:weapon>')
def setWeapon(id, weapon):
    if weapon == 'Unset':
        accounts[id].setWeapon(None)
    else:
        accounts[id].setWeapon(weapon)
    return redirect('/user/%s' % id)

@app.route('/up-weapon-capacity/<string:id>')
def upWeaponCapicity(id):
    accounts[id].refine_queue_capacity += 1
    return redirect('/user/%s' % id)

@app.route('/down-weapon-capacity/<string:id>')
def downWeaponCapicity(id):
    accounts[id].refine_queue_capacity -= 1
    return redirect('/user/%s' % id)

@app.route('/treasure/<string:id>/<string:pos>')
def getTreasure(id, pos='N'):
    accounts[id].gotTreasures()
    b = accounts[id].send('item')['items']
    c = 0
    for i in b:
        if b[i]['itemId'] == 'map_0001':
            accounts[id].send('use', i)
            accounts[id].gotTreasures()
            c += 1
    return "Success! For %d times." % c + redirect_message
    # accounts[id].gotTreasures()
    # if '_' not in pos:
    #     return "Please Specific The position parameters."
    # else:
    #     try:
    #         return str(accounts[id].send('gottreasure', pos)['drop']) + redirect_message
    #     except:
    #         return "Wrong destinition."

@app.route('/target/<string:id>/<string:pos>')
def setTarget(id, pos='N'):
    if '_' not in pos:
        accounts[id].setTarget(None)
        return "Please Specific The destinition parameters."
    else:
        accounts[id].setTarget(pos)
        return "Got it!" + redirect_message

@app.route('/set-interval/<string:id>/<string:interval>')
def setInterval(id, interval='N'):
    if interval == 'N':
        return 'Please specific the interval value.'
    interval = int(interval)
    accounts[id].interval = interval
    accounts[id].print("Change Interval To %d, Interval will effect after next heartbeat" % interval)
    return redirect('/user/' + id)

@app.route('/restart/<string:id>')
def restartUser(id):
    tmp = dict()
    for k in lookuptable:
        try:
            tmp[k] = accounts[id].__dict__[k]
        except:
            pass
    accounts[id] = Account(**tmp)
    return redirect("/user/%s" % id)

@app.route('/')
def index():
    web = ''
    for k in rank_list:
        status = 'green' if accounts[k].active else 'red'
        try:
            if accounts[k].status['position'] == accounts[k].aim:
                status = 'blue'
        except:
            pass
        web += """
        <a href='/user/%s' style='color: %s'>%s</a>
        <br/>
        """ %(k, status, accounts[k].username)
    return web

if __name__ == '__main__':
    app.run()
