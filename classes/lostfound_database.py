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
	def __init__(self, postid, response, userid, sharetime, order=0):
		self.postid = postid
		self.response = response
		self.userid = userid
		self.sharetime = sharetime
		self.order = order


class LFDatabase():
	# Constructor
	def __init__(self, postlist=None):
		self.posts = {}
		self.last_postid = 0

		self.responses = {}
		self.last_responseid = 0

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
			SELECT users.studentno, lostfound.postid, lostfound.sharetime, lostfound.title, users.name, lostfound.LF, lostfound.location 
			FROM lostfound, users
			WHERE (lostfound.userid=users.studentno)
			ORDER BY lostfound.postid DESC;
			"""

		posts = tuple()
		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(select_all_posts_statement)
				posts = cursor.fetchall()

		return posts


	def update_post(self, new_description, postid):
		update_statement = "UPDATE lostfound SET description=%s WHERE postid=%s;"
		args = (new_description, postid)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(update_statement, args)

		return

###########################################################################################################
###########################################################################################################

	#
	# Database management methods for responses table
	#
	def add_response(self, lfresponse):
		self.last_responseid += 1
		self.responses[self.last_responseid] = lfresponse

		insert_statement = "INSERT INTO responses (postid, response, userid, ord, sharetime) VALUES (%s, %s, %s, %s, %s);"
		args = (lfresponse.postid, lfresponse.response, lfresponse.userid, lfresponse.order, lfresponse.sharetime)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(insert_statement, args)
		

	def get_all_responses_for_post(self, postid):
		select_all_responses_statement = """
			SELECT responses.respid, responses.response, responses.userid, responses.ord, responses.sharetime, users.name 
			FROM responses, users
			WHERE (responses.postid=%s AND users.studentno=responses.userid)
			ORDER BY responses.sharetime ASC;
			"""
		args = (postid,)	# one element tuple

		responses = tuple()
		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(select_all_responses_statement, args)
				responses = cursor.fetchall()
				
		return responses

	def delete_response(self, respid):
		if respid in self.responses:
			del self.responses[respid]

		delete_statement = "DELETE FROM responses WHERE respid=%s;"
		args = (respid,)	# single element tuple

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(delete_statement, args)

	def update_response(self, new_message, respid):
		update_statement = "UPDATE responses SET response=%s WHERE respid=%s;"
		args = (new_message, respid)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(update_statement, args)

		return

