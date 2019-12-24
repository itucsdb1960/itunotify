Parts Implemented by Alp Eren Gençoğlu
======================================

The database relations users, lostfound, and responses are implemented and handled by Alp Eren Gençoğlu.
In order to easily handle insertion, deletion, read, and update statement concerning these relations, some classes are constructed.

* To handle users:
	.. code-block:: python
		class User():
			def __init__(self, studentno, name, department, grade, password_hash, personal_info="..."):
				self.studentno = studentno
				self.name = name
				self.department = department
				self.grade = grade
				self.password_hash = password_hash
				self.personal_info = personal_info


		class UserDatabase():
			def __init__(self):
				self.users = {}
				self.last_userid = 0

				file = open(r"heroku_db_url.txt", "r")
				self.dsn = file.read()

* To handle lostfound and responses:
	.. code-block:: python
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
			def __init__(self, postid, response, userid, sharetime, lastupdate, anonymous=False, textcolor="black"):
				self.postid = postid
				self.response = response
				self.userid = userid
				self.sharetime = sharetime
				self.lastupdate = lastupdate
				self.anonymous = anonymous
				self.textcolor = textcolor
				
		class LFDatabase():
			# Constructor
			def __init__(self, postlist=None):
				self.posts = {}
				self.last_postid = 0

				self.responses = {}
				self.last_responseid = 0

				file = open(r"heroku_db_url.txt", "r")
				self.dsn = file.read()

Also related sql tables are created beforehand.
	.. code-block:: sql
		CREATE TABLE IF NOT EXISTS users (
			studentno varchar(10) primary key,
			name varchar(40) NOT NULL,
			department varchar(80),
			grade integer,
			password_hash varchar(256) NOT NULL,
			personal_info VARCHAR(512)
		);
		CREATE TABLE IF NOT EXISTS lostfound (
			postid SERIAL primary key,
			title VARCHAR(32) NOT NULL,
			description VARCHAR(512) NOT NULL,
			userid varchar(10) references users ON DELETE CASCADE ON UPDATE CASCADE,
			LF boolean NOT NULL,
			location VARCHAR(32),
			imageid INTEGER references image(imageid) ON DELETE set default ON UPDATE CASCADE DEFAULT 1,
			sharetime VARCHAR(32)
		);
		CREATE TABLE IF NOT EXISTS responses (
			respid SERIAL primary key,
			postid INTEGER references lostfound(postid) ON DELETE CASCADE ON UPDATE CASCADE,
			response VARCHAR(512) NOT NULL,
			userid varchar(10) references users ON DELETE CASCADE ON UPDATE CASCADE,
			sharetime VARCHAR(32),
			lastupdate VARCHAR(32),
			anonymous boolean DEFAULT FALSE,
			textcolor varchar(16)
		);
				

Register System
---------------
In order to register a new user to the database, user's required information is obtained in the register page.
After user has entered related information and entered values are checked for validity (e.g password length), UserDatabase class' register method is called:
	
	.. code-block:: python
		def register_user(self, user):
        sql_insert_user = """INSERT INTO users (name, department, studentno, grade, password_hash, personal_info) VALUES (
                                %(name)s,
                                %(department)s,
                                %(studentno)s,
                                %(grade)s,
                                %(password_hash)s,
                                %(personal_info)s
                            );"""

        args = {'name': user.name, 'department': user.department, 'studentno': user.studentno,
                'grade': user.grade, 'password_hash': user.password_hash, 'personal_info': user.personal_info};
        with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_insert_user, args)

Profile Page
------------
Once a user's profile page is viewed, following method of UserDatabase class is run to get all data about that user.

	.. code-block:: python
		def get_user_by_userid(self, userid):
			user_query = "SELECT * FROM users WHERE users.studentno=%s"
			args = (userid,)

			with dbapi2.connect(self.dsn) as connection:
				with connection.cursor() as cursor:
					cursor.execute(user_query, args)
					user = cursor.fetchall()
					if len(user) < 1:  # user with _userid_ could not be found
						return None
					else:
						return User(user[0][0], user[0][1], user[0][2], user[0][3], user[0][4], user[0][5])

(Note: From now on, only the sql statement will be provided since all of the python codes for executing sql statements are similar.)
Then, the returned user object is passed to profile.html file and the user's data can be viewed.

	.. code-block:: html
		<h2>Viewing {{userobj.name}}'s profile</h2>
		<label> ID: </label> <p>{{userobj.studentno}}</p>
		<label> Name: </label> <p>{{userobj.name}}</p>
		<label> Department: </label> <p>{{userobj.department}}</p>
		<label> Grade: </label> <p>{{userobj.grade}}</p>
		<label> About {{userobj.name}}: </label> 
		<br><br>
		<p style="white-space: pre-wrap; word-wrap: break-word; margin: 1em;">{{userobj.personal_info}}</p>

	.. figure:: images/appleren/profile_view.PNG
		:scale: 70 %
		:alt: Viewing a profile page

		Viewing a profile page




