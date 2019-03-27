from helper import Account
from time import sleep

# a = Account(
#     'http://xzhkaccount.funthree.com:6913/gamen.j',
#     '49-30-23A273',
#     '869B70F8-D9C5-43E0-9ED8-D2523F7B8E0D',
#     'ef83ffee4a4e8dd53dbcbb6ca732a3ac885380b4d78b72304498a0e0df985e0d'
# )
# b = Account(
#     'http://xzhkaccount.funthree.com:6911/gamen.j',
#     '48-186-11A1027',
#     '4A1591F4-DC0D-45A6-80B3-6E0F2C2AFB26',
#     ''
# )
c = Account(
    'http://xzhkaccount.funthree.com:6913/gamen.j',
    '49-69-10A21',
    '4490DEBA-216D-42CF-ACC0-707A930CB264',
    'cbb5bdc9943ad5ce9d9b359f765f47ac63dbfdee49852726832591a827329602'
)
a = c
while True:
    sleep(10)
    try:
        # print(a.status)
        if a.status['daily_award']:
            a.send('dailyaward')
            print('Get login award - %s' % a.status['name'])
        if a.status['dailyquest_ok_count'] > 0:
            quests = a.getQuest()
            unfinished = 0
            for k in quests:
                if 'dd00' in k:
                    if quests[k]['state'] == 1:
                        unfinished = max(unfinished, int(k[4:]) + 1)
                elif 'd0' in k:
                    if quests[k]['steps'][0]['num'] >= quests[k]['steps'][0]['maxNum']:
                        a.send('finished', k)
            a.send('dd', unfinished)
            print('Get daily award %d - %s' % (unfinished,a.status['name']))
            # print(quests[k]['steps'][0]['num'], quests[k]['steps'][0]['maxNum'])
    except:
        pass
