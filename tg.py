#!/usr/bin/python3
import cgi, requests, json, builtins, sys
builtins.act = 'al'

print('Content-type: text/plain\n')

js = ''

while True:
    try:
        a = input()
        js += a
    except EOFError:
        break
from mysql_aut import *

o = json.loads(js)
mes = o['message']['text']
chat_id = o['message']['chat']['id']
addr = 'https://api.telegram.org/bot{}/sendMessage'.format(open('/var/www/tg_token', 'r').read()[:-1])
mes = mes.replace('"', "&quot;")
mes = mes.replace("'", "&#8217;")
mes = mes.replace("\\", "&#92;")

def sendmes(tresc):
    data = {"text": tresc, "chat_id": chat_id}
    requests.post(addr, data=data)

if mes == '/start':
    data = {"text": "Wprowadź ten numer w formularzu w menu 'Profil': " + str(o['message']['chat']['id']), 'chat_id': o['message']['chat']['id']}
    requests.post(addr, data=data)
    exit()

username = sel_one('select username from notifs where tg="{}"'.format(chat_id))
sid = sel_one('select sid from sessions where username = "{}"'.format(username))
headers = {'Cookie': 'sid='+sid} 
if sid == 0:
    sendmes("Nie jesteś zalogowany do Clicki na żadnym urządzeniu, nie zrobię tego.".format(username))
    exit()

if o['message']['text'][0] == '!':
    adresat = mes.split(' ', 1)[0][1:]
    if adresat == '!':
        adresat = sel_one('select do from messages where od="{}" group by do order by max(czas) desc limit 1'.format(username))
    if adresat not in imiona.keys():
        sendmes('Użytkownik {} nie istnieje.'.format(adresat))
        exit()    
    tresc = mes.replace('!' + adresat + ' ', '')
    data = {'content': tresc}
    requests.post('https://anx.nazwa.pl/xx.py?a=mes_b&z={}'.format(adresat), data=data, headers=headers)
elif mes[0] == '/':
    pass
else:
    adresat = sel_one('select od from messages where do="{}" group by od order by max(czas) desc limit 1'.format(username))
    data = {'content': mes}
    requests.post('https://anx.nazwa.pl/xx.py?a=mes_b&z={}'.format(adresat), data=data, headers=headers)
