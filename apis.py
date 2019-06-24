from flask import Flask, redirect, request, request
from helper import Monitor, Character
from flask_login import LoginManager, login_user, login_required
import json



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
        accounts[cur] = Monitor(**tmp)

@app.route('/')
def index():
    return open('index.html','r').read()

@app.route('/api/listActions')
def listActions():
    return json.dumps(Character.getActions())

@app.route('/api/send', methods=['POST'])
def send():
    req = request.get_json(force=True)
    try:
        accounts[req['uid']].send(req['action'], req['op1'], req['op2'])
        return json.dumps({'code': 'success'})
    except:
        return json.dumps({'code': 'Error'}), 404

@app.route('/api/getList')
def getList():
    r = dict()
    for i in rank_list:
        r[i] = accounts[i].username
    return json.dumps(r)

@app.route('/api/getStatus', methods=['POST'])
def getStatus():
    req = request.get_json(force=True)
    if req['uid'] == 'index':
        r = dict()
        for i in rank_list:
            r[i] = {
                'username': accounts[i].username,
                'active': accounts[i].active,
                'arrived': False
            }
        return json.dumps(r)
    return json.dumps(accounts[req['uid']].character.status)

if __name__ == '__main__':
    app.run()