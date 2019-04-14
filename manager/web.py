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
    'url': 5
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

@app.route('/user/<string:id>')
def user(id):
    result = ''
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
    result += str(accounts[id].status)
    result += "<br/><br/>"
    result += accounts[id].getLogs()
    return result

@app.route('/treasure/<string:id>/<string:pos>')
def getTreasure(id, pos='N'):
    accounts[id].gotTreasures()
    return "Success!" + redirect_message
    if '_' not in pos:
        return "Please Specific The position parameters."
    else:
        try:
            return str(accounts[id].send('gottreasure', pos)['drop']) + redirect_message
        except:
            return "Wrong destinition."

@app.route('/target/<string:id>/<string:pos>')
def setTarget(id, pos='N'):
    if '_' not in pos:
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
        tmp[k] = accounts[id].__dict__[k]
    accounts[id] = Account(**tmp)
    return redirect("/user/%s" % id)

@app.route('/')
def index():
    web = ''
    for k in rank_list:
        web += """
        <a href='/user/%s' style='color: %s'>%s</a>
        <br/>
        """ %(k,'green' if accounts[k].active else 'red', accounts[k].username)
    return web

if __name__ == '__main__':
    app.run()
