import psycopg2 as dbapi2

class User():
	def __init__(self, name, department, studentno, grade, password_hash):
		self.name = name
		self.department = department
		self.studentno = studentno
		self.grade = grade
		self.password_hash = password_hash

class UserDatabase():
	def __init__(self):
		self.users = {}
		self.last_userid = 0

		file = open(r"heroku_db_url.txt", "r")
		self.dsn = file.read()

	def get_user_by_username(self, username):
		user_query = "SELECT * FROM users WHERE users.name=%s"
		args = (username,)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(user_query, args)
				user = cursor.fetchall()
				if len(user) < 1:	# user named _username_ could not be found
					return None
				else:
					return User(user[0][0], user[0][1], user[0][2], user[0][3], user[0][4])
