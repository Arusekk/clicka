#!/usr/bin/python3
from mysql_aut import *
print('Content-type: text/plain\nLocation: xx.py?a=profile\n')

if 'tg' in d:
	if d['tg'] in ('–', '-'):
		d['tg'] = ''
	select('update notifs set tg="{}"where username="{}"'.format(d['tg'], username))
if 'mail' in d:
	if d['mail'] in ('–', '-'):
		d['mail'] = ''
	select('update notifs set mail="{}"where username="{}"'.format(d['mail'], username))
db.commit()
