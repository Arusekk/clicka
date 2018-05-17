#!/usr/bin/python3
import cgi, requests, json, sys

print('Content-type: text/plain\n')

js = ''

while True:
    try:
        a = input()
        js += a
    except EOFError:
        break

o = json.loads(js)

if o['message']['text'][0] == '!':
    adresat = o['message']['text'].split(' ', 1)[0][1:]
    tresc = o['message']['text'].replace('!' + adresat + ' ', '')
    data = {'content': tresc}
    headers = {'Cookie': 'sid='} 
    requests.post('https://anx.nazwa.pl/xx.py?a=mes_b&z={}'.format(adresat), data=data, headers = headers)
else:
    data = {"text": "Wprowadź ten numer w formularzu w menu 'Profil': " + str(o['message']['chat']['id']), 'chat_id': o['message']['chat']['id']}
    requests.post('https://api.telegram.org/bot{}/sendMessage'.format(open('/var/www/tg_token', 'r').read()[:-1]), data=data)
