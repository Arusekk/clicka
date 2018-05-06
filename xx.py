#!/usr/bin/python3
import cgi
import pymysql
import os
import time

print('Content-type: text/html; charset="utf8"')

form = cgi.FieldStorage();
d = dict()
try:
	act = form["a"].value
except KeyError:
	act = 'view'

db = pymysql.connect("localhost", "antek", open("/var/www/mysql_password").read()[:-1], "xx", charset="utf8")
cu = db.cursor()

def select(query):
	cu.execute(query)
	res = cu.fetchall()
	return res

def sel_list(query):
	cu.execute(query)
	res = cu.fetchall()
	l = list()
	for i in res:
		l.append(i[0])
	return l

def sel_one(query):
	return select(query)[0][0]

try:
	a = os.environ['HTTP_COOKIE']
	while len(a) > 4 and not str.startswith(a, 'sid='):
	    a = a[1:]
	b = a.split("=")

	if(b[0] == "sid"):
		sid = b[1]
		for l in sid:
			if l == ';':
				sid = sid.split(';')[0]
				break
			elif l not in 'abcdefghijklmnopqrstuvwxyz':
				print('\nTwój sid jest nieprawdiłowy. Jeśli uważasz, że to nie twoja wina, zgłoś błąd w <a href="https://anx.nazwa.pl:65000/antek/clicka/issues">bug trackerze.</a>')
				print(sid)
				exit()

	cu.execute('select username from sessions where sid = "{}"'.format(sid))
	c = cu.fetchall()
	username = c[0][0]
	try:
		select('insert into activities values ("%s", now(), "%s", "%s")'%(username, os.getenv("REQUEST_URI"), os.getenv('REMOTE_ADDR')))
	except: pass
except Exception as e:
	if act not in ('register', 'register_b', 'login_b'):
		print("Location: xx.cgi\n")
		exit(0)
	username = None

m = {}
fl = open("html").read().splitlines()

for k, v in zip(fl[::2], fl[1::2]):
	m[k] = v

#m['head'] = m['head'].replace("{}", open("style.css").read())

is_uploaded_image = False
image_filename = ""

for i in form:
	if i == "file":

		if form[i].value == b"":
			continue
		if len(form[i].value) > 10**7:
			print("Location: xx.cgi?a=publish&e=img_size\n")
			exit(0)

		sflname = "images/"+str(time.time())+".png"
		while(os.path.isfile(sflname)):
			sflname = "images/"+str(time.time())+".png"
		sfl = open(sflname, "wb")
		sfl.write(form[i].value)

		try:
			from wand.image import Image
			i = Image(filename = sflname)
			if i.width > 300 or i.height > 300:
				i.resize(300, int(i.height*(300/i.width)))
			i.save(filename = sflname)
		except Exception as e:
			os.unlink(sflname)
			print("\n", e)
			print("Location: xx.cgi?a=publish&e=img\n")
			exit(0)
		else:
			is_uploaded_image = True
			image_filename = sflname.replace("images/", "")
		continue

	if i == "pic":
		if form[i].value == b"":
			print("\nWysłano pusty plik.")
			exit(0)
		sflname = "images/"+username
		if(os.path.isfile(sflname)):
			from shutil import move
			move(sflname+'__large.png', sflname+"__!__"+str(time.time()))
		sfl = open(sflname, "wb")
		sfl.write(form[i].value)
		try:
			from wand.image import Image
			img = Image(filename = sflname)
		except Exception as e:
			os.unlink(sflname)
			print("\nPlik <b>nie</b> jest rozpoznawanym obrazkiem")
			exit(0)
		else:
			print("Location: xx.py?a=profile\n")
			select('update users set hasprofilepic = 1 where username = "{}"'.format(username))
			img.format = "png"
			img.resize(200, 200)
			img.save(filename=sflname+'__large.png')
			img.resize(50, 50)
			img.save(filename=sflname+'__medium.png')
			img.resize(25, 25)
			img.save(filename=sflname+'__small.png')
			db.commit()
			exit(0)
	try:
		v = form[i].value
	except KeyError:
		print('\n\n', form[i])
		exit(0)
	#if i == 'pswd1' or i == 'pswd2' or i == 'passwd':
	#	for j in range(len(v)):
	#		if ord(v[j]) not in range(32, 126):
	#			v = v.replace(v[j], '*')

	v = cgi.escape(v)
	v = v.replace('"', "&quot;")
	v = v.replace("'", "&#8217;")
	v = v.replace("\\", "&#92;")
	d[i] = v;

cu.execute("select username, imie from users")
res = cu.fetchall()
imiona = {res[i][0]: res[i][1] for i in range(0, len(res))}
belonging_groups = [int(x) for x in sel_list('select groupid from group_belonging where user="{}"'.format(username))]
nazwy_grup_l = select('select id, nazwa from groups')
nazwy_grup = {str(x[0]): str(x[1]) for x in nazwy_grup_l}

def postsbysql(query, where='a=view', display_from_open_groups = False):
	#czy nowe wiadomości; nieodebrane wiadomości:
	od = select('select od from seen where do="{}" and unseen!=0'.format(username))
	for i in od:
		print('<h2 style="color: red">Masz nowe nieodebrane wiadomości od <a href="xx.py?a=mes&z=%s" onclick="location.reload()" target="_blank"><u>%s</u></a></h2>'%(i[0], imiona[i[0]]))
	#
	#wyzwania szachy:
	challenges = select('select id, biale, czarne from chess where (biale="{u}" or czarne="{u}") and parent="propo" and proponent!="{u}"'.format(u=username))
	for c in challenges:
		proponent = (c[1] if c[1] != username else c[2])
		print('<h2 style="color: red">{p} proponuje ci grę w szachy ♔♘. <a href="xx.py?a=challenge_b&resp=accept&id={id}" style="color: green; text-decoration: underline" target="_blank">Przyjmij</a> albo też <a href="xx.py?a=challenge_b&resp=decline&id={id}" style="color: orange; text-decoration: underline">odrzuć</a></h2>'.format(p=imiona[proponent], id=c[0]))
	#
	#otwarte gry szachy:
	gry = select('select id, biale, czarne, parent from chess where (biale="{u}" or czarne="{u}") and parent!="propo" and wynik=0 and turn="{u}"'.format(u=username))
	for g in gry:
		opponent = (g[1] if g[1] != username else g[2])
		occasion = (' w ramach ' + g[3] + ' ' if g[3] != 'challenge_accepted' else '') 
		print('<h2 style="color: red">Jest twój ruch w grze z <a href="xx.py?a=chess&id=%s" target="_blank"><u>%s</u></a>%s</h2>'%(g[0], imiona[opponent], occasion))
	#

	for i in select(query):
		a = str(i[4])
		while a != "" and a[-1] == "\n":
			a = a[:-1]

		post_id = i[0]
		author = i[6]
		parent_t = i[2]
		parent = i[3]
		img = i[5]
		if str(parent_t) == '2' and str(parent) not in [str(x) for x in belonging_groups]:
			if not display_from_open_groups:
				continue

		likes = select('select count(user) from likes where parent_t = 0 and parent = "{}" and value = 1'.format(i[0]))[0][0]
		dislikes = select('select count(user) from likes where parent_t = 0 and parent = "{}" and value = 0'.format(i[0]))[0][0]
		likers = sel_list('select user from likes where parent_t = 0 and parent = "{}" and value = 1'.format(i[0]))
		dislikers = sel_list('select user from likes where parent_t = 0 and parent = "{}" and value = 0'.format(i[0]))
		likers_s = ""
		dislikers_s = ""
		for i in likers:
			likers_s += imiona[i] + "\n"
		for i in dislikers:
			dislikers_s += imiona[i] + "\n"

		# ▶➤
		print('<div class="post" id="{}"><div class="author"><img src="xx.py?a=img&img=_profile_{}&size=medium"><span class="author_name">{}'.format(post_id, author, imiona[author]))
		if str(parent_t) == '1':
			print(' ➤ {}</span></div>'.format(imiona[parent])) 
			#target
		elif str(parent_t) == '2':
			print(' ➤ {}</span></div>'.format(nazwy_grup[parent]))
		else:
			print('</span></div>')
		if str(img) != "0":
			print('<img src="xx.py?a=img&img={}" style="margin-bottom: 20px">'.format(img))
		print('<div class="content">', a, '</div>')
		print('<div class="likebox">')
		print('<span class="like" id="{}_l" title="{}" onclick="like(0,{},1)">Aprobuję ({})</span></a>'.format(post_id, likers_s, post_id, likes))
		print('<span class="dislike" id="{}_dl" title="{}" onclick="like(0,{},0)">Dezaprobuję ({})</span></a></div>'.format(post_id, dislikers_s, post_id, dislikes))

		#komentarze:
		comments = select('select * from comments where parent=%d'%post_id)
		#comments_count = sel_list('select count(*) from comments where parent=%d'%post_id)[0]
		print('''<div class="commentsbox" onclick="show_comments({})">Napisz komentarz</div>'''.format(post_id))
		
		# if(int(comments_count) in range(1, 4)):
		# 	print('<div class="comments" id="c{}" lt3>'.format(post_id))
		# else:
		# 	print('<div class="comments" id="c{}">'.format(post_id))

		print('<div class="comments" id="c{}">'.format(post_id))

		for n, i in enumerate(comments):
			if n:
				print('<br>')
			print('<span class="comment"><img src="xx.py?a=img&img=_profile_{}&size=small">'.format(i[0]))
			print(' <b>{}</b> {}</span>'.format(imiona[i[0]], i[3]))

		print('''<form action="xx.py?a=comment_b&w={post_id}" method="post" autocomplete="off" class="comment_form" id="c_f_{post_id}">
			<input type="text" name="content" value=" Napisz komentarz…" class="itext" style="width: 100%" onclick="comment_onclick(this)">
		</form>'''.format(post_id=post_id))
		print('</div>')		
		print('</div>')
	print('<span id="bottom"></span>')
	try:
		print('<a href=xx.py?{}&weeks={}#bottom><h3>Pokaż starsze posty…</h3></a>'.format(where, int(d['weeks']) + 10 ))
	except: pass

if act == "publish_b":
	if d['target'] == "group":
		parent_t = 2
		parent = d['group']
		cu.execute('insert into contents values(0, 1, {}, "{}", "{}", "{}", "{}", now(), now())'.format(parent_t, parent, d['content'], image_filename if is_uploaded_image else 0, username))
	elif d['target'] == "space" or d['target'] == "myspace":
		parent_t = 1
		if d['target'] == 'myspace':
			parent = username
		else:
			parent = d['space']
		cu.execute('insert into contents values(0, 1, {}, "{}", "{}", "{}", "{}", now(), now())'.format(parent_t, parent, d['content'], image_filename if is_uploaded_image else 0, username))
	elif d['target'] == 'public':
		parent_t = 0
		parent = 0
		cu.execute('insert into contents values(0, 1, {}, {}, "{}", "{}", "{}", now(), now())'.format(parent_t, parent, d['content'], image_filename if is_uploaded_image else 0, username))

	db.commit()
	print("Location: xx.cgi\n") #TODO: raczej tam gdzie wysłałeś post, ale może też nie, jak ci się chce
	exit(0)

elif act == "view":
	print()
	print(m['head'], m['body_o'])
	for i in belonging_groups:
		print(m['entryp_o'].replace('{}', 'group&id={}'.format(i)), nazwy_grup[str(i)],'</a></div>')
	print("</div>", m['main_o'])

	#postsbysql('select * from contents where datediff(now(), date) <= 7*{} order by date desc'.format(d['weeks']))
	d.setdefault('weeks', 6)
	postsbysql('select * from contents order by date desc limit {}'.format(d['weeks']))

elif act == "like_b":
	resp = 'inni'
	select('delete from likes where user="{}" and parent_t = "{}" and parent="{}"'.format(username, d['parent_t'], d['parent']))
	select('insert into likes values("{}", {}, "{}", now(), {})'.format(username, d['parent_t'], d['parent'], d['v']))
	
	if d['v'] == '1':
		resp = select('select count(user) from likes where parent_t = 0 and parent = "{}" and value = 1'.format(i[0]))[0][0]
	else:
		resp = select('select count(user) from likes where parent_t = 0 and parent = "{}" and value = 0'.format(i[0]))[0][0]
	print()
	print(resp)

elif act == "comment_b":
	select('insert into comments values ("%s", %d, now(), "%s")'%(username, int(d['w']), d['content']))
	select('update contents set date = now() where id = %s'%d['w'])
	print('Location: xx.py?a=view#%d\n'%int(d['w']))

elif act == "logout":
	select('delete from sessions where sid = "{}"'.format(sid))
	print("Location: xx.cgi\n")

elif act == "profile":
	print()
	print(m['head'], m['body_o'], "</div>", m['main_o']) #TODO: wypisz grupy, w view już zrobiono
	print(m['profile'])

elif act == "invite_b":
	import random
	link = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(10))
	select('insert into invitations values ("{}", "{}", "{}", now(), 1, 0)'.format(username, d['whom'], link))
	print()
	print(m['head'], m['body_o'], "</div>", m['main_o']) #TODO: wypisz grupy
	print('Wyślij zaproszonej osobie link do rejestracji:<br><h4>https://anx.nazwa.pl/xx.py?a=register&id={}</h4>'.format(link))

elif act == 'mes_b':
	if not set(d['content']) <= set('\n\t '):
		select('insert into messages values(0, "{}", "{}", "{}", now(), 0)'.format(username, d['z'], d['content']))
		#widoczność:
		l = select('select unseen from seen where od="{}" and do="{}"'.format(username, d['z']))
		if not len(l):
			select('insert into seen set od="{}", do="{}", unseen=1'.format(username, d['z']))
		else:
			select('update seen set unseen = unseen + 1 where od="{}" and do="{}"'.format(username, d['z']))
	print('Location: xx.py?a=mes&z=%s\n'%d['z'])

elif act == 'anm': #are new messages
	print()
	try:
		unseen = sel_one('select unseen from seen where od="{}" and do="{}"'.format(d['z'], username))
	except IndexError:
		unseen = 0
	if unseen == 0:
		print(0)
		exit()
	else:
		print(1)
		exit()

elif act == "anm_chess": #are new moves
	print()
	try:
		last_chess_query = sel_list('select czas from last_chess_query where username="%s" and game_id=%s'%(username, d['gameid']))[0]
		last_move_time = sel_list('select last_move_t from chess where id=%s'%d['gameid'])[0]
	except (IndexError, KeyError):
		print(1)
		exit()

	if(last_chess_query < last_move_time):
		print(1)
	else:
		print(0)

elif act == 'messages':
	print()
	try:
		unseen = sel_one('select unseen from seen where od="{}" and do="{}"'.format(d['z'], username))
	except (IndexError):
		unseen = 0
	d.setdefault('weeks', 12)
	d['weeks'] = max(d['weeks'], unseen)

	messages = select('(select content, od, czas from messages where (od = "{u}" and do = "{z}") or (od = "{z}" and do = "{u}") order by czas desc limit {weeks}) order by czas asc'.format(weeks = d['weeks'], u = username, z = d['z']))
	for mes in messages:
		if mes[1] == username:
			otag = m['mymes_o']
		else:
			otag = m['almes_o']
		otag = otag.replace('{time}', str(mes[2]))
		print(otag, mes[0], '<br></span><br>')

	select('update seen set unseen = 0 where od="{}" and do="{}"'.format(d['z'], username))

elif act == "mes":
	print()
	d.setdefault('z', sel_one('select do from messages where od = "{}" group by do order by count(czas) desc limit 1;'.format(username)))
	
	print(m['head'], m['body_o'], '<script>z = "{}"</script>'.format(d['z']))
	rozmowcy = sel_list('select od from messages where do="{u}" group by od order by max(czas) desc limit 10'.format(u=username))
	for r in rozmowcy:
		print(m['entryp_o'].replace('{}', 'mes&z=' + r), imiona[r], '</div></a>')

	print('</div>', m['main_o'])
	print('<span id="messages">\n</span>')

	print(m['mes_form'], m['audios'])
	print("<h3 style=\"color: green\">Wiadomości odświeżają się same.</h3>")
	
elif act == "groups":
	print()
	print(m['head'], m['body_o'])
	for i in belonging_groups:
		print(m['entryp_o'].replace('{}', 'group&id={}'.format(i)), nazwy_grup[str(i)],'</a></div>')
	print("</div>", m['main_o'])
	print('<h3><a href="xx.py?a=create_group"><u>Stwórz</u></a> własną grupę</h3>')

	for i in select('select * from groups where typ != 2'):
		print('<a href="xx.py?a=group&id=%s">'%i[0], m['enum_o'], i[1], '<br>')
		print('<span class="desc">', i[3], '</span><br><span class="desc">Admin: %s</span>'%imiona[i[5]]) 	
		if int(i[2]) == 1:
			print(m['group_o_img'])
		else:
			print(m['group_c_img'].replace('{}', imiona[i[5]]))
		
		print('</div></a><br>')

elif act == "group":
	belonging_groups = sel_list('select groupid from group_belonging where user="{}"'.format(username))
	group_type = sel_list('select typ from groups where id=%s'%d['id'])[0]
	
	if int(d['id']) not in belonging_groups and group_type not in (1, '1'):
		print("\n<h1>Nie należysz do tej grupy!</h1>")
		#print(belonging_groups)
		exit(0)

	print("\n", m['head'], m['body_o'], "</div>", m['main_o']) #TODO: wypisz grupy, w view już zrobiono
	print('<h1><u>{}</u></h1>'.format(nazwy_grup[d['id']]))
	group_admin = sel_list('select admin from groups where id=%s'%d['id'])[0]
	if group_admin == username:
		print('<h3>Jesteś administratorem tej grupy. <a href="xx.py?a=panel&g=%s"><u>Zarządzaj członkami.</u></a></h3>'%d['id'])
	if group_type in (1, '1') and int(d['id']) not in belonging_groups:
		print('<h3>Nie należysz do tej otwartej grupy. <a href="xx.py?a=group_add&groupid=%s&whom=%s&return=group"><u>Dołącz do grupy</u></a></h3>'%(d['id'], username))

	d.setdefault('weeks', 6)
	postsbysql('select * from contents where parent_t = 2 and parent = "{}" order by date desc limit {}'.format(d['id'], d['weeks']), where='a=group&id=%s'%d['id'], display_from_open_groups = True)

elif act == "panel":
	group_admin = sel_list('select admin from groups where id=%s'%d['g'])[0]
	if group_admin != username:
		print('\n<h1>Nie jesteś administratorem tej grupy!</h1>')
		exit()

	print("\n<h3>Do grupy należą:</h1>")
	members = sel_list("select user from group_belonging where groupid=%s"%d['g'])
	for i in members:
		print(imiona[i], '<a href="xx.py?a=group_rem&groupid={}&whom={}">Usuń</a>'.format(d['g'], i),"<br>")

	print('<h3>Dodaj do grupy:</h3>')
	for i in imiona.keys():
		if i not in members:
			print('<a href="xx.py?a=group_add&groupid={}&whom={}">'.format(d['g'], i), imiona[i], '</a><br>')
	print('<a href="xx.py?a=group&id=%s"><h3>Powrót</h3></a>'%d['g'])

elif act == "group_add":
	group_admin = sel_list('select admin from groups where id=%s'%d['groupid'])[0]
	group_type = sel_list('select typ from groups where id=%s'%d['groupid'])[0]

	if group_admin != username and group_type not in (1, '1'):
		print('\n<h1>Nie jesteś administratorem tej grupy!</h1>')
		exit()

	select('insert into group_belonging values(%s, "%s", now())'%(d['groupid'], d['whom']))
	try:
		if d['return']== 'group':
			print('Location: xx.py?a=group&id=%s\n'%d['groupid'])
	except KeyError:
		print('Location: xx.py?a=panel&g=%s\n'%d['groupid'])

elif act == "group_rem":
	group_admin = sel_list('select admin from groups where id=%s'%d['groupid'])[0]
	if group_admin != username:
		print('<h1>Nie jesteś administratorem tej grupy!</h1>')
		exit()

	select('delete from group_belonging where groupid=%s and user="%s"'%(d['groupid'], d['whom']))
	print('Location: xx.py?a=panel&g=%s\n'%d['groupid'])

elif act == "myspace":
	print('Location: xx.py?a=space&user=%s\n'%username)

elif act == 'space':
	uid = d['user']
	print()
	print(m['head'], m['body_o'], "</div>", m['main_o']) #TODO: wypisz grupy

	if uid not in sel_list('select username from users'):
		print("<h1>Zażądany użytkownik nie istnieje.</h1>")
		exit(0)

	print('<div style="display: block"><img style="float: none" src="xx.py?a=img&img=_profile_%s&size=large"><h1>%s</h1><br></div>'%(uid, imiona[uid]))
	d.setdefault('weeks', 6)
	postsbysql('select * from contents where parent_t = 1 and parent = "%s" order by date desc limit %s'%(uid, d['weeks']), where='a=space&user=%s'%uid)

elif act == "register":
	print()
	res = select('select count(whom) from invitations where link = "{}" and active = 1'.format(d['id']))
	try:
		1/int(res[0][0])
	except (IndexError, ZeroDivisionError):
		print('Link do zaproszenia nie został rozpoznany albo jest już nieaktywny')
		exit(0)

	print(m['head'], m['register'].replace("{}", d['id']))

elif act == "register_b":
	res = select('select count(whom) from invitations where link = "{}" and active = 1'.format(d['id']))
	try:
		1/int(res[0][0])
	except (IndexError, ZeroDivisionError):
		print('\nLink do zaproszenia nie został rozpoznany albo jest już nieaktywny')
		exit(0)
	try:
		if len(d['username']) > 128:
			print("\nZbyt długa nazwa, nie może przekraczać 128 znaków")
			exit(0)

		import string
		for i in d['username']:
			if i not in string.ascii_letters + string.digits:
				print("\nTylko znaki a-z A-Z 0-9 są dozwolone w nazwie użytkownika")
				exit(0)

		if d['username'] in sel_list('select username from users'):
			print("\nNazwa jest już zajęta.")
			exit(0)

		if d['pswd1'] != d['pswd2']:
			print("\nHasła się nie zgadzają.")
			exit(0)

		if len(d['imie'].encode('utf-8')) >= 300:
			print("\nImię użytkownika jest zbyt długie")
			exit(0)

		if d['imie'] in sel_list('select imie from users'):
			print("\nImię, które podałeś, jest już zajęte. Pamiętaj, że nie wolno podszywać się pod osoby, którymi nie jesteś, oraz że twoje imię musi umożliwiać innym zidentyfikowanie cię")

	except KeyError:
		print('\nWszystkie pola są obowiązkowe.')
		exit(0)

	import hashlib
	sha = hashlib.sha256()
	sha.update(d['pswd1'].encode('utf-8'))
	pswd = sha.hexdigest().upper()
	select('update invitations set active = 0 where link = "{}"'.format(d['id']))
	select('update invitations set registered = now() where link = "{}"'.format(d['id']))
	select('insert into users values("{}", "{}", "{}", 0, "{}")'.format(d['username'], pswd, d['imie'], d['id']))
	select('insert into last_mes_query values("{}", now())'.format(d['username']))
	print("Location: xx.cgi\n")
	print('\n')

elif act == 'create_group':
	print()
	print(m['head'], m['body_o'], "</div>", m['main_o']) #TODO: wypisz grupy
	print(m['create_group'])

elif act == 'create_group_b':
	if d['nazwa'] in sel_list('select nazwa from groups'):
		print("\nNazwa jest już zajęta :(")
		exit(0)

	d.setdefault('opis', '')

	select('insert into groups values(0, "%s", %d, "%s", 0, "%s")'%(d['nazwa'], int(d['typ']), d['opis'], username))
	groupid = sel_list('select id from groups where nazwa = "%s"'%d['nazwa'])[0]
	select('insert into group_belonging values(%d, "%s", now())'%(int(groupid), username))
	print('Location: xx.py?a=groups\n')

elif act == 'img':
	import sys
	sys.stdout.buffer.write(b'Content-type: image/png\n')

	#if 'size' in d and d['size'] == '__system':
	#	sys.stdout.buffer.write(b'Cache-control: max-age=1000000\n\n')
	#	sys.stdout.buffer.write(open('system_images/'+d['img'], 'rb').read())
	#	exit()
	
	if str.startswith(d['img'], '_profile_'):
		sys.stdout.buffer.write(b'Cache-control: max-age=604800\n\n')
		profusr = d['img'].replace('_profile_', '')
		hasprofilepic = int(select('select hasprofilepic from users where username = "%s"'%profusr)[0][0])
		if hasprofilepic == 1:
			sys.stdout.buffer.write(open('images/%s__%s.png'%(profusr, d['size']), 'rb').read())
		else:
			#sys.stdout.buffer.write(open('images/__implementation__default.png', 'rb').read())
			sys.stdout.buffer.write(open('images/__implementation__default__%s.png'%(d['size']), 'rb').read())
		exit(0)
	else:
		sys.stdout.buffer.write(b'Cache-control: max-age=1000000000\n\n')
		p_t, p = select('select parent_t, parent from contents where img = "%s"'%d['img'])[0]
		if p_t == 2 and int(p) not in belonging_groups:			
			exit(0)
		sys.stdout.buffer.write(open('images/%s'%d['img'], 'rb').read())
		exit(0)

elif act == "login_b":
	login = d['login']
	passwd = d['passwd']
	# ok = False
	import hashlib
	sha = hashlib.sha256()
	sha.update(passwd.encode('utf-8'))
	hashed = sha.hexdigest().upper()

	s = select('select username, imie from users where username="%s" and passwd="%s"'%(login, hashed))
	try:
		username = s[0][0]
	except IndexError:
		print('\nNieprawidłowy login lub hasło :(')
		exit()

	import random
	sid = ''.join(chr(random.choice(range(ord('a'), ord('z')+1))) for x in range(127))
	select('delete from sessions where username="%s"'%login)
	select('insert into sessions values("%s", "%s", now(), 0)'%(sid, login))
	print('Set-Cookie: sid=%s'%sid)
	print('Location: xx.py?a=view\n')
	print("Ok")

elif act == "chess":
	# print('Content-type: text/plain')
	print()
	print(m['head'], m['body_o'], '</div>', m['main_o'], m['audios'])
	print('<script>id = %s</script>'%d['id'])
	select('delete from last_chess_query where  username = "%s" and game_id=%s'%(username, d['id']))
	select('insert into last_chess_query set czas = now(), username = "%s", game_id=%s'%(username, d['id']))

	import chess, chess.svg
	start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
	fen, last_move, result, time_limit, biale_t, czarne_t, last_move_t = select('select stan, last_move, wynik, time_limit, biale_t, czarne_t, last_move_t from chess where id=%s'%d['id'])[0]
	bcq = select('select biale, czarne from chess where id=%s'%d['id'])[0]
	if (bcq[0] == username):
		user_color = True
		opponent = bcq[1] 
	elif (bcq[1] == username):
		user_color = False
		opponent = bcq[0]
	elif public:
		usercolor = 'spectator'
	else:
		print('\n<h1>Ta gra nie jest publiczna</h1>')
		exit()

	b = chess.Board(fen=fen)
	
	if(b.is_check()):
		checked_king = b.king(b.turn)
		is_check = True
	else:
		is_check = False
		checked_king = None

	flipped = not	user_color
	svg = chess.svg.board(b, size=450, lastmove=chess.Move.from_uci(last_move), check=checked_king, flipped=flipped, coordinates=not not not True)
	rects = ''
	if not flipped:
		for row, y in zip(range(8, 0, -1), range(0, 360, 45)):
			for col, x in zip(list('abcdefgh'), range(0, 360, 45)):
				rects += '<rect id="{id}" height="45" fill="red" opacity="0" width="45" x="{x}" y="{y}" onclick="zaznacz_pole(this.id);"/>'.format(id=col + str(row), x=x, y=y)
	if flipped:
		for row, y in zip(range(1, 9), range(0, 360, 45)):
			for col, x in zip(list('hgfedcba'), range(0, 360, 45)):
				rects += '<rect id="{id}" height="45" fill="red" opacity="0" width="45" x="{x}" y="{y}" onclick="zaznacz_pole(this.id);"/>'.format(id=col + str(row), x=x, y=y)
	svg = svg[:-6] + rects + svg[-5:]

	if(result == 1):
		print('<h1 style="margin: 0">Zwyciężył(a) <span style="color: white">%s</span></h1>' % (imiona[username] if user_color else imiona[opponent]))
		if not b.is_game_over():
			print('<h2>Gracz zrezygnował</h2>')
			if time_limit:
				print('<h2>albo przekroczył czas gry</h2>')
	elif(result == -1):
		print('<h1 style="margin: 0">Zwyciężył(a) <span style="color: black">%s</span></h1>' % (imiona[username] if not user_color else imiona[opponent]))
		if not b.is_game_over():
			print('<h2>Gracz zrezygnował</h2>')
			if time_limit:
				print('<h2>albo przekroczył czas gry</h2>')
	elif is_check:
		print('<h1 style="color: red">Szach</h1>')
	if user_color == b.turn and not result:
		print('<h2>Jest twoja kolej.</h2>')
	elif not result:
		print('<h2>Jest kolej przeciwnika.</h2>')

	# wyświetlanie zegarów:
	if time_limit and biale_t > 0 and czarne_t > 0:
		import datetime, time
		now = datetime.datetime.fromtimestamp(time.time())
		elapsed = int((now - last_move_t).total_seconds())
		if(last_move_t > now):
			print('Ta gra rozpocznie się o {}'.format(str(last_move_t)))
			exit()
		if b.turn:
			biale_t -= elapsed
		else:
			czarne_t -= elapsed
		biale_timer = '[' + str(datetime.timedelta(seconds = biale_t)).replace('days', 'dni') + ']'
		czarne_timer = '[' +  str(datetime.timedelta(seconds = czarne_t)).replace('days', 'dni') + ']'
		upper_t, lower_t = biale_timer, czarne_timer
		if user_color:
			upper_t, lower_t = lower_t, upper_t
	else:
		upper_t = lower_t = ''

	print('<h2><img src="xx.py?a=img&img=_profile_%s&size=medium" style="float: none">   %s %s</h2>'%(opponent, imiona[opponent], upper_t))
	print(svg)
	print('<h2><img src="xx.py?a=img&img=_profile_%s&size=medium" style="float: none">   %s %s</h2>'%(username, imiona[username], lower_t))

	#print(chess.svg.piece(chess.BaseBoard(board_f0en=b.board_fen()).piece_at(chess.C1), size=20))
	#można dodać wyświetlanie zbitych bierek

elif act == "chess_b":
	import chess

	fen, history, result, public, biale_t, czarne_t, time_limit, last_move_t = select('select stan, history, wynik, public, biale_t, czarne_t, time_limit, last_move_t from chess where id=%s and (biale="%s" or czarne="%s")'%(d['id'], username, username))[0]
	bcq = select('select biale, czarne from chess where id=%s'%d['id'])[0]
	if (bcq[0] == username):
		user_color = True
		opponent = bcq[1] 
	elif bcq[1] == username:
		user_color = False
		opponent = bcq[0]
	else:
		exit()

	#rezygnowanie:
	if "r" in d.keys() and d['r'] == 'resign':
		select('update chess set wynik="{w}" where id={id}'.format(w=(-1 if user_color else 1), id=d['id']))
		db.commit()
		print('Location: xx.py?a=mygames\n')
		exit()
	#

	move_s = d['from'] + d['to']
	b = chess.Board(fen=fen)
	#move = chess.Move(chess.square(int(d['from'][0]), int(d['from'][1])), chess.square(int(d['to'][0]), int(d['to'][1])), promotion=chess.QUEEN)
	move = chess.Move.from_uci(move_s)
	movep = chess.Move.from_uci(move_s + 'q')

	if(b.result() != '*' or result != 0):
		print('\nTa gra jest już zakończona.')
		print(b.result())
		exit()

	if(user_color != b.turn):
		print('\n<h1>Nie jest twoja kolej.</h1><a href="xx.py?a=chess&id=%s">Powrót</a>'%d['id'])
		exit()

	#czas w grach zegarowych 
	if time_limit:
		import datetime, time
		now = datetime.datetime.fromtimestamp(time.time())
		elapsed = int((now - last_move_t).total_seconds())
		if last_move_t > now:
			print('\n<h1>Ta gra rozpoczyna się {}'.format(str(last_move_t)))
			exit()
		if b.turn:
			select('update chess set biale_t = %d where id=%s'%(biale_t - elapsed, d['id']))
			if biale_t - elapsed <= 0:
				select('update chess set wynik = -1 where id=%s'%d['id'])
				print('Location: xx.py?a=chess&id=%s\n'%d['id'])
				db.commit()
				exit()
		else:
			select('update chess set czarne_t = %d where id=%s'%(czarne_t - elapsed, d['id']))
			if czarne_t - elapsed <= 0:
				select('update chess set wynik = 1 where id=%s'%d['id'])
				print('Location: xx.py?a=chess&id=%s\n'%d['id'])
				db.commit()
				exit()

	if movep in b.legal_moves:
		move = movep
	if move in b.legal_moves:
		if type(history) == type(None):
			history = ''
		history = history + str(b.san(move)) + ' '
		b.push(move)
		turn = (bcq[0] if b.turn else bcq[1])
		select('update chess set stan = "%s", last_move="%s", history="%s", turn="%s", last_move_t = now() where id=%s'%(b.fen(), move, history, turn, d['id']))
		if(b.result() != '*'):
			#print("\n", b.result())
			if(b.result() == '1-0'):
				select('update chess set wynik = %d where id=%s'%(1, d['id']))
			elif(b.result() == '0-1'):
				select('update chess set wynik = %d where id=%s'%(-1, d['id']))
	else:
		print()
		if(b.is_into_check(move) or b.is_into_check(movep)):
			print('<h1>Ten ruch umieści twojego króla w szachu.</h1>')
		print('<h1>Ten ruch nie jest dozwolony</h1><a href="xx.py?a=chess&id=%s">Powrót</a>'%d['id'])
		exit()

	print('Location: xx.py?a=chess&id=%s'%d['id'])
	print()

elif act == "challenge_b":
	if 'whom' in d.keys():
		import random
		biale, czarne = username, d['whom']
		if random.randint(0, 1):
			biale, czarne = czarne, biale
		select('insert into chess set biale = "%s", czarne = "%s", proponent="%s", parent="propo" '%(biale, czarne, username))
		print('\n', m['head'], m['body_o'], '</div>', m['main_o'], '<h1>Zaproszono użytkownika do gry</h1></div>')
	elif 'id' in d.keys():
		if d['resp'] == 'accept':
			select('update chess set parent="challenge_accepted", start_time = now() where id=%s'%(d['id']))
			print('Location: xx.py?a=chess&id=%s\n'%d['id'])
		elif d['resp'] == 'decline':
			select('delete from chess where id=%s'%d['id'])
			print('Location: xx.py?a=view\n')
	else:
		print()
		print(d)

elif act == "mygames":
	print()
	print(m['head'], m['body_o'], '</div>', m['main_o'])
	print('<h1>Twoje gry:</h1>')
	mygames = select('select id, biale, czarne, wynik, turn, history, parent from chess where (biale="{u}" or czarne="{u}") and parent!="propo" order by start_time desc'.format(u=username))
	mygames = sorted(mygames, key=lambda x: 0 if x[3] == 0 or x[6] != 'challenge_accepted' else 1)
	for g in mygames:
		opponent = (g[1] if g[1] != username else g[2])
		user_color = (1 if g[1] == username else -1)
		if g[3] == 0:
			stan = '<span style="color: red">Trwająca</span>'
		elif g[3] == user_color:
			stan = '<span style="color: green">Wygrana</span>'
		elif g[3] == 12:
			stan = 'Zremisowana'
		else:
			stan = '<span style="color: blue">Przegrana</span>'
		print('<h3><a href="xx.py?a=chess&id=%s">'%g[0], stan, ' gra z ', imiona[opponent], '</a>')
		if g[6] != 'challenge_accepted':
			print(' w ramach', g[6])
		if not g[3]:
			print('<a href="xx.py?a=chess_b&r=resign&id={id}">[zrezygnuj]</a>'.format(id=g[0]))
		print('<a href="xx.py?a=game_history&id={id}">[pokaż historię]</a></h3>'.format(id=g[0]))

elif act == "game_history":
	import chess, chess.svg
	print()
	game = select('select biale, czarne, history from chess where id={id} and (biale="{u}" or czarne="{u}")'.format(u=username, id=d['id']))
	if not len(game):
		print('<h1>Ta gra nie jest publiczna i nie jesteś jej członkiem albo ta gra w ogóle nie istnieje.</h1>')
		exit()
	print('Biale:', imiona[game[0][0]], '<br>')
	print('Czarne:', imiona[game[0][1]], '<br>')
	b = chess.Board()
	for i in game[0][2].split():
		print(i, '<br>')
		b.push_san(i)
		print(chess.svg.board(b, size=200), '<br>')

#VARIA:

# elif act == "stats":
# 	print()
# 	print('<title>Statystyki</title><body style="text-align: center; background-color: #dcd2b6"><img src="h.png"><h1>Statystyki Clicki</h1>')
# 	visitors_today = sel_list('select count(distinct username) from activities where cast(date as date) = curdate()')[0]
# 	posts_today = sel_list('select count(id) from contents where cast(czas as date) = curdate()')[0]
# 	comments_today = sel_list('select count(date) from comments where cast(date as date) = curdate()')[0]
# 	messages_today = sel_list('select count(id) from messages where cast(czas as date) = curdate()')[0]
# 	by_mes = select('select od, count(id) from messages group by od')

# 	print('<h4>Clickę odwiedziło dzisiaj %s, którzy napisali %s postów, %s komentarzy i %s wiadomości.</h4>'%(visitors_today, posts_today, comments_today, messages_today))
# 	print('<h3>Użytkownicy wg napisanych wiadomości:</h3>')
# 	print('<table style="border: solid 1px black">')
# 	for i in by_mes:
# 		print('<tr><td>', imiona[i[0]], '</td><td>', i[1], '</td></tr>')
# 	print('</table>')	
# 	print('</body>')


else:
	print('\n', m['nieznany_act'])

db.commit()
