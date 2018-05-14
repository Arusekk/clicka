import subprocess as sb, requests
from mysql_aut import *

tg_token = open('/var/www/tg_token').read().replace('\n', '')

class Notifiee:
	def __init__(self, un):
		try:
			self.tg, self.mail, self.settings = select('select tg, mail, settings from notifs where username="{}"'.format(un))[0]
		except IndexError:
			self.tg, self.mail, self.settings = 3*[None]
	def send(self, text, traits):
		if self.mail not in ('', None):
			sb.Popen(['/usr/sbin/sendmail', '-fclicka', self.mail], stdin=sb.PIPE).communicate(text)
		if self.tg not in ('', None):
			data = {'chat_id': self.tg, 'text': text, 'parse_mode': 'Markdown'}
			r = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(tg_token), data=data)
			response = r.text

def notify(notifiees, text, traits=None):
	for n in notifiees:
		Notifiee(n).send(text, traits)
