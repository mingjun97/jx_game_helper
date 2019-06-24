from urllib import request
from urllib.parse import urlencode
from time import sleep, localtime, strftime, time
from threading import Thread

from .account import Character
from .config import servers, secret_key

import os
cwd = os.getcwd()

class Monitor:
    def __init__(self, user_id, server='ios2', interval=10, **kwargs):
        del(kwargs['url'])
        self.character = Character(servers[server], user_id, **kwargs)
        self.user_id = user_id
        self.username = kwargs['username']

        self.active = True
        self.active_thread = 0
        self.last_active = time()
        self.interval = int(interval)

        self.position_notified = False
        self.resource_alert = False

        self.only_best = False
        self.refine_queue_capacity = 1

        self.aim = None


        try:
            with open('%s/logs/%s.log' % (cwd, user_id), 'r') as log_fp:
                self.logs = "\n\n\n----------- Saved log ------------\n" + log_fp.read()
        except:
            self.logs = ''
        self.character.update(retry=True)
        self.last_heartbeat = ''
        self.log("Monitor Started.")

        Thread(target=self.monitor).start()
        Thread(target=self.guard).start()




    def log(self, message, *args):
        l = '\n[%s] %s' % (
                    strftime("%Y-%m-%d %H:%M:%S", localtime()),
                    message % args
        )
        self.logs += l
        try:
            with open('%s/logs/%s.log' % (cwd, self.user_id), 'a') as logs:
                logs.write(l)
        except:
            pass

    def notify(self, title, desp = ""):
        req = request.Request("https://sc.ftqq.com/%s.send" % secret_key,
         data=urlencode({b"text": ("%s - %s" % (title, self.username)).encode('utf-8') , 
                         b"desp": desp.encode('utf-8')}
                        ).encode('utf-8'))
        request.urlopen(req)
    
    def guard(self):
        while self.active:
            if (time() - self.last_active) > (self.interval * 4.0):
                    Thread(target=self.monitor).start()
                    self.log("Guard detected potential timeout occurred. Perform restart!")
            sleep(self.interval / 2.0)

    def monitor(self):
        failed = 0
        self.active_thread += 1
        me = self.active_thread
        while self.active:
            if me != self.active_thread:
                self.log("Duplicated thread! Thread-%d exited to avoid wasting!", me)
                return
            self.last_active = time()
            try:
                failed += 1
                self.character.update(True)
                failed = 0
            except:
                self.log('Update failed.. Try again.. Current attempts count: %d', failed)
                if failed >= 3:
                    self.active = False
                    self.notify('oO掉线通知Oo - %s' % self.user_name, desp="Monitor检测到")
                sleep(3)
                continue

            sleep(self.interval)
            
    def send(self, action, op1=None, op2=None):
        return self.character.send(action, op1, op2)

    def getLog(self):
        return self.logs.replace('\n', '<br/>')