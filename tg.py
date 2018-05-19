#!/usr/bin/python3
import cgi, requests, json, builtins
builtins.act = 'al'
from mysql_aut import *

print('Content-type: text/plain\n')

js = ''

while True:
    try:
        a = input()
        js += a
    except EOFError:
        break

o = json.loads(js)
mes = o['message']['text']
chat_id = mes = o['message']['chat']['id']
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
elif o['message']['text'][0] == '!':
    adresat = mes.split(' ', 1)[0][1:]
    tresc = mes.replace('!' + adresat + ' ', '')
    data = {'content': tresc}
    username = sel_one('select username from notifs where tg="{}"'.format(chat_id))
    sid = sel_one('select sid from session where username = "{}"'.format(username))
    if sid == 0:
        sendmes("Trzeba być zalogowanym, by móc wysyłać wiadomości.")
        exit()
    headers = {'Cookie': 'sid='+sid} 
    requests.post('https://anx.nazwa.pl/xx.py?a=mes_b&z={}'.format(adresat), data=data, headers=headers)