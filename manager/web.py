from flask import Flask
import flask_login
from helper import Account

accounts = dict()

app = Flask(__name__)

lookuptable = {
    'username': 0,
    'user_id': 1,
    'device_id': 2,
    'gdevice_id': 3,
    'interval': 4,
    'url': 5
}

def lookup(d, k):
    return d[lookuptable[k]]

with open('account.csv') as b:
    a = b.read().replace('\ufeff', '')
for i in a.split('\n'):
    if len(i) > 5:
        record = i.split(',')
        cur = lookup(record, 'user_id')
        tmp = dict()
        for k in lookuptable:
            tmp[k] = lookup(record, k)
        accounts[cur] = Account(**tmp)

@app.route('/user/<string:id>')
def user(id):
    result = ''
    result += str(accounts[id].status)
    result += "<br/><br/>"
    result += accounts[id].getLogs()
    return result

@app.route('/')
def index():
    web = ''
    for k in accounts:
        web += """
        <a href='/user/%s'>%s</a>
        <br/>
        """ %(k, accounts[k].username)
    return web

app.run()
