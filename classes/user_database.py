import psycopg2 as dbapi2


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

    #
    # INSERT QUERY
    #
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


    #
    # READ (SELECT) QUERIES
    #
    def get_user_by_username(self, username):
        user_query = "SELECT * FROM users WHERE users.name=%s"
        args = (username,)

        with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(user_query, args)
                user = cursor.fetchall()
                if len(user) < 1:  # user named _username_ could not be found
                    return None
                else:
                    return User(user[0][0], user[0][1], user[0][2], user[0][3], user[0][4], user[0][5])

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

    def get_userid_by_username(self, username):
    	userid_query = "SELECT users.studentno FROM users WHERE users.name = %s"
    	args = (username,)                

    	with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(userid_query, args)
                return cursor.fetchone()[0]


    #
    # UPDATE QUERIES
    #
    def update_user_attrs(self, user):
        update_statement = "UPDATE users SET name=%s, department=%s, grade=%s WHERE studentno=%s;"
        args = (user.name, user.department, user.grade, user.studentno)

        with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(update_statement, args)

        return        

    def update_user_password(self, new_passhash, userid):
        update_statement = "UPDATE users SET password_hash=%s WHERE studentno=%s;"
        args = (new_passhash, userid)

        with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(update_statement, args)

        return

    def update_personal_info(self, new_personal_info, userid):
        update_statement = "UPDATE users SET personal_info=%s WHERE studentno=%s;"

        args = (new_personal_info, userid)

        with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(update_statement, args)

        return

    #
    # DELETE QUERY
    #
    def delete_user(self, userid):
        delete_statement = "DELETE FROM users WHERE studentno=%s;"
        args = (userid,)    # single element tuple

        with dbapi2.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.execute(delete_statement, args)

        return