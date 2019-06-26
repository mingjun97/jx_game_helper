from flask import Flask, redirect, request
from helper import Account
from flask_login import LoginManager, login_user, login_required

from threading import Thread

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
app.secret_key = b'_5#y2L"F4?.Q8z\n\xec]/'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader

class User():
    is_authenticated = True
    is_active = True 
    is_anonymous = False
    def __init__(self, uid):
        self.uid = uid
    def get_id(self):
        return ("%d" % self.uid).encode('utf-8')

def load_user(user_id):
    return User(user_id)

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

@app.route('/manual-weapon/<string:id>')
def manualWeapon(id):
    Thread(target=accounts[id].cleanWeapon).start()
    return "Sent!" + redirect_message

@app.route('/login', methods=['GET'])
def login():
        return """
<form method='POST'>
    <input name='username'/><br/>
    <input name='password' type='password'/><br/>
    <input type='submit' value='login'/>
</form>"""

@app.route('/login', methods=['POST'])
def login_post():
    if request.form['username'] == 'mingjun97' and request.form['password'] == 'hu3tc4':
        login_user(User(1))
    return redirect('/')


@app.route('/user/autostudy/<string:id>')
@login_required
def setAutostudy(id):
    accounts[id].setAutostudy()
    return redirect('/user/%s' % id)

@app.route('/user/automove/<string:id>')
@login_required
def setAutomove(id):
    accounts[id].setAutomove()
    return redirect('/user/%s' % id)

@app.route('/user/<string:id>/save')
@login_required
def save(id):
    accounts[id].saveConfig()
    return redirect('/user/%s' % id)

@app.route('/newbie/<string:id>/<int:times>')
def activeNewbie(id, times):
    Thread(target=accounts[id].activeNewbie, args=(times,)).start()
    return "Sent! " + redirect_message

@app.route('/user/<string:id>/load')
@login_required
def load(id):
    accounts[id].readConfig()
    return redirect('/user/%s' % id)

@app.route('/user/<string:id>')
@login_required
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

    result += '<a href="/refresh_weapon/%s">Weapons(Fly)</a>: ' % id
    result += "<br/>"



    try:
        result += \
            ("" if not accounts[id].fly_sword else '[<a style="color: %s" href="/fly_with/%s/N">%s+%d</a>]&nbsp;&nbsp;' % (['gray', 'green', 'blue', 'red'][accounts[id].weapons[accounts[id].fly_sword]['quality'] - 1],
            id, accounts[id].weapons[accounts[id].fly_sword]['weaponId'], accounts[id].weapons[accounts[id].fly_sword]['level']))
        for i in accounts[id].weapons:
            result += '<a href="/fly_with/%s/%s" style="color: %s">%s+%d</a> &nbsp;&nbsp;' % (id,i, 
            ['gray', 'green', 'blue', 'red'][accounts[id].weapons[i]['quality'] - 1],
            accounts[id].weapons[i]['weaponId'], accounts[id].weapons[i]['level'])
    except:
        pass
    result += "<br/>"

    result += '<a href="/newbie/%s/1">1 NEWBIE</a> &nbsp;&nbsp;' % id
    result += '<a href="/newbie/%s/5">5 NEWBIE</a> &nbsp;&nbsp;' % id
    result += '<a href="/newbie/%s/10">10 NEWBIE</a> &nbsp;&nbsp;' % id
    
    result += "<br/>"
    result += "<br/>"

    result += '<a href="/manual-weapon/%s">Manual Clean Weapon</a>' %id

    result += "<br/>"
    result += "<br/>"
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

@app.route('/refresh_weapon/<string:id>')
@login_required
def refresh_weapon(id):
    accounts[id].refresh_weapons()
    return redirect('/user/%s' % id)

@app.route('/fly_with/<string:id>/<string:wid>')
@login_required
def fly_with(id, wid):
    if wid != 'N':
        accounts[id].fly_sword = wid
    else:
        accounts[id].fly_sword = None
    return redirect('/user/%s' % id)

@app.route('/only-best/<string:id>')
@login_required
def onlyBest(id):
    accounts[id].only_best = 1
    return redirect('/user/%s' % id)

@app.route('/set-weapon/<string:id>/<string:weapon>')
@login_required
def setWeapon(id, weapon):
    if weapon == 'Unset':
        accounts[id].setWeapon(None)
    else:
        accounts[id].setWeapon(weapon)
    return redirect('/user/%s' % id)

@app.route('/up-weapon-capacity/<string:id>')
@login_required
def upWeaponCapicity(id):
    accounts[id].refine_queue_capacity += 1
    return redirect('/user/%s' % id)

@app.route('/down-weapon-capacity/<string:id>')
@login_required
def downWeaponCapicity(id):
    accounts[id].refine_queue_capacity -= 1
    return redirect('/user/%s' % id)

@app.route('/treasure/<string:id>/<string:pos>')
@login_required
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
@login_required
def setTarget(id, pos='N'):
    accounts[id].transport = False
    if '_' not in pos:
        accounts[id].setTarget(None)
        return "Please Specific The destinition parameters."
    else:
        accounts[id].setTarget(pos)
        return "Got it!" + redirect_message

@app.route('/set-interval/<string:id>/<string:interval>')
@login_required
def setInterval(id, interval='N'):
    if interval == 'N':
        return 'Please specific the interval value.'
    interval = int(interval)
    accounts[id].interval = interval
    accounts[id].print("Change Interval To %d, Interval will effect after next heartbeat" % interval)
    return redirect('/user/' + id)

@app.route('/restart/<string:id>')
@login_required
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
@login_required
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
