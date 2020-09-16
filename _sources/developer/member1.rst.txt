Parts Implemented by Alp Eren Gençoğlu
======================================

The database relations users, lostfound, and responses are implemented and handled by Alp Eren Gençoğlu.
In order to easily handle insertion, deletion, read, and update statement concerning these relations, some classes are constructed.

- To handle users:

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

- To handle lostfound and responses:

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

Also related sql tables are created beforehand:

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
Once a user's profile page is viewed, following method of UserDatabase class is run to get all data about that user:

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

* (Note: From this point on, only the sql statement will be provided since all of the python codes for executing sql statements are similar.)

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

Example:		

	.. figure:: images/appleren/profile_view.PNG
		:scale: 50 %
		:alt: Viewing a profile page

		Viewing a profile page


If a user is viewing their own profile page, they can modify their data or delete their account by using the forms in the page.
SQL statement to modify name, department or grade (in the related method of UserDatabase class):
	
	.. code-block:: sql
	
		UPDATE users SET name=%s, department=%s, grade=%s WHERE studentno=%s;
		
		
SQL statement to modify personal information (in the related method of UserDatabase class):
	
	.. code-block:: sql
	
		UPDATE users SET personal_info=%s WHERE studentno=%s;
		
		
SQL statement to modify password (in the related method of UserDatabase class):
	
	.. code-block:: sql
	
		UPDATE users SET password_hash=%s WHERE studentno=%s;
		
		
SQL statement to delete entire account from the database (in the related method of UserDatabase class):
	
	.. code-block:: sql
	
		DELETE FROM users WHERE studentno=%s;

		
Lost & Found Page
-----------------
In the Lost & Found page, when a user (if logged in) uses the form to share a post, following sql statement is executed by using LFDatabase class' related method.

.. code-block:: sql

	INSERT INTO lostfound (title, description, userid, LF, location, imageid, sharetime) VALUES (%s, %s, %s, %s, %s, %s, %s);

Python code that calls the method mentioned above:

 .. code-block:: python
	
	# new post created from /lostfound
	if form_name == "new_post":
		if not session.get("is_loggedin", False):   # if not logged in, log in :)
			flash("You must login first to do that!", "error")
			return redirect("/login")

		title = request.form.get("title")
		if len(title) > 32:
			title = title[:29] + "..."
		description = request.form.get("description")
		userid = session["userid"]
		LF = request.form.get("LF")
		location = request.form.get("location")

		if title == "" or description == "" or LF == None:
			return render_template("lost_and_found.html", posts=posts)
		else:
			timestamp = getTimestampString()
			lfpost = LFPost(title, description, userid, LF, location=location, sharetime=timestamp)
			lf_db.add_post(lfpost)
			posts = lf_db.get_all_posts()
			current_app.config["LF_DB"] = lf_db
			return redirect("/lostfound")

In the main page, below the form to submit posts, there is a table which shows the recent posts' titles and some other data. This table's content is generated by the following method of LFDatabase class:

.. code-block:: python

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

And the table is created with the following html (Since location is optional, it may be null when passed to the html file. If null "---" is written on the table):

.. code-block:: html

	<table class="lfposts" id="lfposts_table">
		<tr>
			<th onclick="sortTable('sharetime')"> Share Time </th>
			<th onclick="sortTable('title')"> Title </th>
			<th onclick="sortTable('username')"> Shared by </th>
			<th onclick="sortTable('category')"> Category </th>
			<th onclick="sortTable('location')"> Location </th>
		</tr>
		{% for userid, postid, sharetime, title, username, LF, location in posts %}
		<tr>
			<td> {{sharetime}} </td>
			<td class="title"> <a class="lfpost_link" href="/lostfound/{{postid}}">{{ title }}</a> </td>
			<td> <a class="profile_link" href="/profile/{{userid}}">{{ username }}</a> </td>
			<td> {% if LF %} Found {% else %} Lost {% endif %} </td>
			<td> {% if location %} {{ location }} {% else %} --- {% endif %} </td>
		</tr>
		{% endfor %}
	</table>

As it can be seen from the code above, the table can be sorted by clicking on the column headers. Script for sorting the table can be found in the lost_and_found.html file.


When a post's title is clicked, the server redirects user to that specific post's page. In this page, the post's data is obtained by using the following sql statement of the related method of LFDatabase class:

.. code-block:: sql

	SELECT * FROM lostfound WHERE lostfound.postid=%s;

Example:
	.. figure:: images/appleren/lfpost_view.png
		:scale: 50 %
		:alt: Viewing a Lost & Found post

		Viewing a Lost & Found post


The posts' and responses' description part can be edited by the original posters. Once the Edit button is clicked, a new form will appear and once Update button is clicked, following codes are executed for post and response respectively:

.. code-block:: python

	elif form_name == "update_post":
		postowner_userid = request.form.get("userid")
		if not session.get("userid") == postowner_userid:
			flash("You do not have authentication to do that!", "error")
			return redirect("/lostfound/{}".format(postid))

		new_description = request.form.get("new_description")
		lf_db.update_post(new_description, postid)
		flash("Post description is updated successfully.", "info")
		return redirect("/lostfound/{}".format(postid))

.. code-block:: python

	def update_post(self, new_description, postid):
		update_statement = "UPDATE lostfound SET description=%s WHERE postid=%s;"
		args = (new_description, postid)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(update_statement, args)

		return


.. code-block:: python

	elif form_name == "update_response":
            respowner_userid = request.form.get("userid")
            if not session.get("userid") == respowner_userid:
                flash("You do not have authentication to do that!", "error")
                return redirect("/lostfound/{}".format(postid))

            respid = request.form.get("respid")
            new_message = request.form.get("new_response")
            timestamp = getTimestampString()

            lf_db.update_response(new_message, timestamp, respid)
            flash("Response is updated successfully.", "info")
            return redirect("/lostfound/{}".format(postid))

.. code-block:: python

	def update_response(self, new_message, update_time, respid):
		update_statement = "UPDATE responses SET response=%s, lastupdate=%s WHERE respid=%s;"
		args = (new_message, update_time, respid)

		with dbapi2.connect(self.dsn) as connection:
			with connection.cursor() as cursor:
				cursor.execute(update_statement, args)

		return



Additionals
-----------
Since it is impossible to explain whole code here, some of the functions are shortened. For further analysis; *user_database.py, lostfound_database.py* files **and** *lostfound_page, lfpost_page, register_page, profile* functions from server.py can be examined.

















