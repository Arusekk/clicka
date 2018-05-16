import pymysql, os, cgi

try:
	db
except NameError:
	db = pymysql.connect("localhost", "antek", open("/var/www/mysql_password").read()[:-1], "xx", charset="utf8")
	cu = db.cursor()

try:
	d
except (NameError):
	form = cgi.FieldStorage();
	d = dict()
	try:
		act = form["a"].value
	except KeyError:
		act = 'view'
	for i in form:
		v = form[i].value
		v = cgi.escape(v)
		v = v.replace('"', "&quot;")
		v = v.replace("'", "&#8217;")
		v = v.replace("\\", "&#92;")
		d[i] = v;

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
	try:
		return select(query)[0][0]
	except:
		return 0

try:
	username
except NameError:
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
		#import metacircles
    #dome = metacircles.Dome(username)
		try:
			select('insert into activities values ("%s", now(), "%s", "%s")'%(username, os.getenv("REQUEST_URI"), os.getenv('REMOTE_ADDR')))
		except KeyError: pass
	except (KeyError, IndexError, NameError):
		if act not in ('register', 'register_b', 'login_b'):
			print("Location: xx.cgi\n")
			exit(0)
		username = None
