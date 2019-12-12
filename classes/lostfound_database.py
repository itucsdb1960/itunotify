from copy import copy
import psycopg2 as dbapi2

class LFPost():
	def __init__(self, title, description, userid, LF, location=None, imageid=1, sharetime=None):
		self.title = title
		self.description = description
		self.userid = userid
		self.LF = LF
		self.location = location
		self.imageid = imageid
		self.sharetime = sharetime

class LFResponse():
	def __init__(self, postid, response, userid, order, sharetime):
		self.postid = postid
		self.response = response
		self.userid = userid
		self.order = order
		self.sharetime = sharetime


class LFDatabase():
	# Constructor
	def __init__(self, postlist=None):
		self.posts = {}
		self.last_postid = 0

		file = open(r"heroku_db_url.txt", "r")
		self.dsn = file.read()
	
	#
	# Database management methods for lostfound table
	#
	def	add_post(self, lfpost):
		self.last_postid += 1
		self.posts[self.last_postid] = lfpost

		insert_statement = "INSERT INTO lostfound (title, description, userid, LF, location, imageid, sharetime) VALUES (%s, %s, %s, %s, %s, %s, %s);"
		args = (lfpost.title, lfpost.description, lfpost.userid, lfpost.LF, lfpost.location, lfpost.imageid, lfpost.sharetime)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(insert_statement, args)


	def delete_post(self, postid):
		if postid in self.posts:
			del self.posts[postid]

		delete_statement = "DELETE FROM lostfound WHERE postid=%s;"
		args = (postid,)	# single element tuple

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(delete_statement, args)

	def get_post(self, postid):
		select_post_statement = "SELECT * FROM lostfound WHERE lostfound.postid=%s;"
		select_username_statement = "SELECT users.name FROM lostfound, users WHERE (lostfound.postid=%s) AND (lostfound.userid=users.studentno);"
		args = (postid,)

		lfpost = None
		extra_info = {"postid":postid}
		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(select_post_statement, args)
				pid, tit, desc, uid, lf, loc, imid, stime  = cursor.fetchone()
				lfpost = LFPost(tit, desc, uid, lf, loc, imid, stime)
				cursor.execute(select_username_statement, args)
				extra_info["username"] = cursor.fetchone()[0]	# fetchone returns a tuple even if result is one element only

		# lfpost = copy(self.posts.get(postid))
		return lfpost, extra_info

	def get_all_posts(self):
		select_all_posts_statement = """
			SELECT lostfound.postid, lostfound.sharetime, lostfound.title, users.name, lostfound.LF, lostfound.location 
			FROM lostfound, users
			WHERE (lostfound.userid=users.studentno)
			ORDER BY lostfound.postid DESC;
			"""

		posts = tuple()
		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(select_all_posts_statement)
				posts = cursor.fetchall()
				# for pid, tit, name, lf, loc in cursor:
				# 	post = LFPost()

		# posts = copy(self.posts)
		return posts


	#
	# Database management methods for responses table
	#
	def add_response(self):
		pass
