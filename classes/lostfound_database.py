from copy import copy
import psycopg2 as dbapi2

class LFPost():
	def __init__(self, title, description, userid, LF, location=None, imageid=None):
		self.title = title
		self.description = description
		self.userid = userid
		self.LF = LF
		self.location = location
		self.imageid = imageid


class LFDatabase():
	# Constructor
	def __init__(self, postlist=None):
		self.posts = {}
		self.last_postid = 0

		file = open(r"heroku_db_url.txt", "r")
		self.dsn = file.read()

	# Database management methods
	def	add_post(self, lfpost):
		self.last_postid += 1
		self.posts[self.last_postid] = lfpost

		insert_statement = "INSERT INTO lostfound (title, description, userid, LF, location, imageid) VALUES (%s, %s, %s, %s, %s, %s);"
		args = (lfpost.title, lfpost.description, lfpost.userid, lfpost.LF, lfpost.location, lfpost.imageid)

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
		lfpost = copy(self.posts.get(postid))
		return lfpost

	def get_all_posts(self):
		select_all_posts_statement = """
			SELECT lostfound.title, users.name, lostfound.LF, lostfound.location 
			FROM lostfound, users;
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
