from flask import Flask, current_app, render_template, request, session, flash, redirect, url_for

# Importing custom classes
from classes.store_database import StoreDatabase
from classes.sell_item import SellItem
from classes.lostfound_database import LFPost, LFDatabase
from classes.user_database import User, UserDatabase

import dbinit

import psycopg2 as dbapi2
from hashlib import sha256  # hashing passwords

import random  # for tests


# <old> app = Flask(__name__)
connection_string = "dbname='postgres' user='postgres' password='postgrepass' host='localhost' port=5432"

app = Flask(__name__)


store_db = StoreDatabase()
lf_db = LFDatabase()
user_db = UserDatabase()


app.config["STORE_DB"] = store_db
app.config["LF_DB"] = lf_db
app.config["USER_DB"] = user_db

# return app


#""" <old>
@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/lostfound", methods=["POST", "GET"])
def lostfound_page():
    lf_db = current_app.config["LF_DB"]
    posts = lf_db.get_all_posts()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        userid = random.randint(1, 3)
        LF = request.form.get("LF")
        location = request.form.get("location")

        if title == "" or description == "" or LF == None:
            return render_template("lost_and_found.html", posts=posts)
        else:
            lfpost = LFPost(title, description, userid, LF, location=location)
            lf_db.add_post(lfpost)
            posts = lf_db.get_all_posts()
            current_app.config["LF_DB"] = lf_db

    return render_template("lost_and_found.html", posts=posts)


@app.route("/store", endpoint='store_page', methods=["POST", "GET"])
def store_page():
    store_db = current_app.config["STORE_DB"]
    selling_items = store_db.get_all_selling_items()
    return render_template("store.html", selling_items=sorted(selling_items))


@app.route("/lostfound/<int:postid>", methods=["POST", "GET"])
def lfpost_page(postid):
    lf_db = current_app.config["LF_DB"]
    post, extra = lf_db.get_post(postid)
    responses = None
    return render_template("lfpost.html", post=post, extra=extra, responses=responses)


@app.route("/register", methods=["POST", "GET"])
def register_page():
    user_db = current_app.config["USER_DB"]

    if request.method == "POST":
        user_name = request.form.get("username")
        user_department = request.form.get("department")
        user_studentno = request.form.get("studentno")
        user_grade = request.form.get("grade")
        user_password = request.form.get("password1")
        password_check = request.form.get("password2")

        if(password_check != user_password):
            # passwords dont match
            return redirect(url_for('register_page'))

        user_password_hash = sha256(user_password.encode()).hexdigest()
        user = User(user_name, user_department, user_studentno, user_grade, user_password_hash)

        user_db.register_user(user)

        return redirect(url_for('home_page'))

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login_page():
    print(session)
    user_db = current_app.config["USER_DB"]

    if request.method == "POST":
        username = request.form.get("username")
        user = user_db.get_user_by_username(username)
        if user == None:
            return redirect("/login")

        password = request.form.get("password")
        if password != user.password_hash:
            return redirect("/login")

        session["username"] = username
        session["is_loggedin"] = True

        return redirect("/")

    return render_template("login.html")

#</old> """


if __name__ == "__main__":
    # dbinit.initialize(connection_string)
    #app = create_app(app)
    app.run(debug=True)
