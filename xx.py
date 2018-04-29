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
except:
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
		print(e)
		print(sid)
		exit(0)
	username = None

m = dict();
fl = open("html").read().splitlines()

for i in range(0, len(fl), 2):
	m[fl[i]] = fl[i+1]

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
		v = form[i].value;
	except:
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
	last_mes_query = sel_list('select czas from last_mes_query where username="%s"'%username)[0]
	last_rec_mes = select('select czas, od from messages where do="%s" order by czas desc'%username)
        	
	unread_displayed = set()

	for j in last_rec_mes:
		if last_mes_query < j[0] and j[1] not in unread_displayed:
			print('<h2 style="color: red">Masz nowe nieodebrane wiadomości od <a href="xx.cgi?a=mes&z=%s" onclick="location.reload()" target="_blank"><u>%s</u></a></h2>'%(j[1], imiona[j[1]]))
			unread_displayed.add(j[1])
			#m['body_o'] = m['body_o'].replace('<div class="fixed_entry">Wiadomości</div>', '<div class="fixed_entry" style="background:red">Wiadomości</div>')
		else:
			break;
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
		comments_count = sel_list('select count(*) from comments where parent=%d'%post_id)[0]
		print('''<div class="commentsbox" onclick="show_comments({})">Pokaż komentarze ({})</div>'''.format(post_id, comments_count))
		
		if(int(comments_count) in range(1, 4)):
			print('<div class="comments" id="c{}" lt3>'.format(post_id))
		else:
			print('<div class="comments" id="c{}">'.format(post_id))

		for n, i in enumerate(comments):
			if n:
				print('<br>')
			print('<span class="comment"><img src="xx.py?a=img&img=_profile_{}&size=small">'.format(i[0]))
			print(' <b>{}</b> {}</span>'.format(imiona[i[0]], i[3]))

		print('''<form action="xx.py?a=comment_b&w={}" method="post" autocomplete="off">
			<input type="text" name="content" value=" Napisz komentarz…" class="itext" style="width: 100%" onclick="comment_onclick(this)">
		</form>'''.format(post_id))
		print('</div>')		
		print('</div>')
	print('<span id="bottom"></span>')
	try:
		print('<a href=xx.py?{}&weeks={}#bottom><h3>Pokaż starsze posty…</h3></a>'.format(where, int(d['weeks']) + 20	))
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

	try:
		d['weeks']
	except:
		d['weeks'] = 6
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
	print('Location: xx.cgi?a=mes&z=%s\n'%d['z'])

elif act == 'anm': #are new messages
	print()
	last_mes_query = sel_list('select czas from last_mes_query where username="%s"'%username)[0]
	last_message_time = sel_list('''select czas from messages where 
		((od = "{u}" and do = "{z}") or (od = "{z}" and do = "{u}")) order by czas desc limit 1'''.format(czas = int(last_mes_query.timestamp()),u = username, z = d['z']))[0]
	if(last_mes_query < last_message_time):
		print(1)
	else:
		print(0)

elif act == 'messages':
	print()
	
	last_mes_query = sel_list('select czas from last_mes_query where username="%s"'%username)[0]
	dates_before_query = sel_list('''select count(id) from messages where 
		((od = "{u}" and do = "{z}") or (od = "{z}" and do = "{u}")) and czas > from_unixtime({czas})'''.format(czas = int(last_mes_query.timestamp()),u = username, z = d['z']))[0]
	try:
		d['weeks']
	except:
		d['weeks'] = 12
	d['weeks'] = max(d['weeks'], dates_before_query)

	messages = select('(select content, od, czas from messages where (od = "{u}" and do = "{z}") or (od = "{z}" and do = "{u}") order by czas desc limit {weeks}) order by czas asc'.format(weeks = d['weeks'], u = username, z = d['z']))
	for mes in messages:
		if mes[1] == username:
			otag = m['mymes_o']
		else:
			otag = m['almes_o']
		otag = otag.replace('{time}', str(mes[2]))
		print(otag, mes[0], '<br></span><br>')
	
	select('delete from last_mes_query where username = "{}"'.format(username))
	select('insert into last_mes_query values ("{}", now())'.format(username))

elif act == "groups":
	print()
	print(m['head'], m['body_o'])
	for i in belonging_groups:
		print(m['entryp_o'].replace('{}', 'group&id={}'.format(i)), nazwy_grup[str(i)],'</a></div>')
	print("</div>", m['main_o'])
	print('<h3><a href=\"xx.py?a=create_group\"><u>Stwórz</u></a> własną grupę</h3>')

	for i in select('select * from groups where typ != 2'):
		print('<a href="xx.py?a=group&id=%s">'%i[0], m['enum_o'], i[1], '<br>')
		print('<span class="desc">', i[3], '</span>') 	
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

	postsbysql('select * from contents where parent_t = 2 and parent = "{}" order by date desc'.format(d['id']), where='a=group&id=%s'%d['id'], display_from_open_groups = True)

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
	except:
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
	
	postsbysql('select * from contents where parent_t = 1 and parent = "%s" order by date desc limit %s'%(uid, d['weeks']), where='a=space&user=%s'%uid)
	#...

elif act == "register":
	print()
	res = select('select count(whom) from invitations where link = "{}" and active = 1'.format(d['id']))
	try:
		1/int(res[0][0])
	except:
		print('Link do zaproszenia nie został rozpoznany albo jest już nieaktywny')
		exit(0)

	print(m['head'], m['register'].replace("{}", d['id']))

elif act == "register_b":
	res = select('select count(whom) from invitations where link = "{}" and active = 1'.format(d['id']))
	try:
		1/int(res[0][0])
	except:
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

		if(d['pswd1'] != d['pswd2']):
			print("\nHasła się nie zgadzają.")
			exit(0)

		if(len(d['imie'].encode('utf-8'))) >= 300:
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

	try:
		d['opis']
	except KeyError:
		d['opis'] = ''

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
		hasprofilepic = select('select hasprofilepic from users where username = "%s"'%profusr)[0][0]
		if hasprofilepic in (1, '1'):
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
	except:
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
	#print('Content-type: text/plain')
	print()
	print('<script src="jquery.js"></script>')
	print('<script src="script.js"></script>')
	print('<script>id = %s</script>'%d['id'])

	import chess, chess.svg
	start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
	fen, last_move = select('select stan, last_move from chess where id=%s'%d['id'])[0]
	bcq = select('select biale, czarne from chess where id=%s'%d['id'])[0]
	if (bcq[0] == username):
		user_color = True
		opponent = bcq[1] 
	else:
		user_color = False
		opponent = bcq[0]

	b = chess.Board(fen=fen)
	
	if(b.is_check()):
		checked_king = b.king(b.turn)
		is_check = True
	else:
		is_check = False
		checked_king = None

	print('<h2><img src="xx.py?a=img&img=_profile_%s&size=medium">   %s</h2>'%(opponent, imiona[opponent]))
	print(chess.svg.board(b, size=400, lastmove=chess.Move.from_uci(last_move), check=checked_king, flipped=not user_color))
	print('<h2><img src="xx.py?a=img&img=_profile_%s&size=medium">   %s</h2>'%(username, imiona[username]))

elif act == "chess_b":
	import chess

	q,w,e,r = d['move']
	move = ''.join([w,q,r,e])
	fen = select('select stan from chess where id=%s'%d['id'])[0][0]
	bcq = select('select biale, czarne from chess where id=%s'%d['id'])[0]
	if (bcq[0] == username):
		user_color = True
		opponent = bcq[1] 
	else:
		user_color = False
		opponent = bcq[0]

	b = chess.Board(fen=fen)
	move = chess.Move.from_uci(move)

	if(user_color != b.turn):
		print('Location: xx.py?a=chess&id=%s\n'%d['id'])
		exit()

	if move in b.legal_moves:
		b.push(move)
		select('update chess set stan = "%s", last_move="%s" where id=%s'%(b.fen(), move, d['id']))
	else:
		#print('\n<h1>Nie jest to dozwolony ruch!</h1>')
		pass

	print('Location: xx.py?a=chess&id=%s'%d['id'])
	print()

#VARIA:

elif act == "stats":
	print()
	print('<title>Statystyki</title><body style="text-align: center; background-color: #dcd2b6"><img src="h.png"><h1>Statystyki Clicki</h1>')
	visitors_today = sel_list('select count(distinct username) from activities where cast(date as date) = curdate()')[0]
	posts_today = sel_list('select count(id) from contents where cast(czas as date) = curdate()')[0]
	comments_today = sel_list('select count(date) from comments where cast(date as date) = curdate()')[0]
	messages_today = sel_list('select count(id) from messages where cast(czas as date) = curdate()')[0]
	by_mes = select('select od, count(id) from messages group by od order by count(id) desc')

	print('<h4>Clickę odwiedziło dzisiaj %s użytkowników, którzy napisali %s postów, %s komentarzy i %s wiadomości.</h4>'%(visitors_today, posts_today, comments_today, messages_today))
	print('<h3>Użytkownicy wg wysłanych wiadomości:</h3>')
	print('<table style="border: solid 1px black">')
	for i in by_mes:
		print('<tr><td>', imiona[i[0]], '</td><td>', i[1], '</td></tr>')
	print('</table>')	
	print('</body>')

else:
	print('\n', m['nieznany_act'])

db.commit()
