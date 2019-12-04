from flask import Flask, current_app, render_template, request
#import views
from classes.store_database import StoreDatabase
from classes.sell_item import SellItem
from classes.lostfound_database import LFPost, LFDatabase
import dbinit

#import psycopg2
from hashlib import sha256  # hashing passwords

import random  # for tests


# <old> app = Flask(__name__)
connection_string = "dbname='postgres' user='postgres' password='postgrepass' host='localhost' port=5432"

app = Flask(__name__)


# def create_app(app):
#app = Flask(__name__)

#app.add_url_rule("/", view_func=views.home_page)
#app.add_url_rule("/lostfound", view_func=views.lostfound_page, methods=["POST", "GET"])
#app.add_url_rule("/store", view_func=views.store_page, endpoint='store_page', methods=["POST", "GET"])

store_db = StoreDatabase()
lf_db = LFDatabase()

# --- initialization tests ---
# sellItem1 = SellItem("fridge", 100, "alp", 3, 6, shortD="buy please", image="fridge image")
# sellItem2 = SellItem("horse", 99999999, "horseman", 0, 0)
# store_db.add_selling_item(sellItem1)
# store_db.add_selling_item(sellItem2)

# lfpost1 = LFPost("Black Watch", "Black analog watch found in MED", 3, True, location="MED", imageid=None)
# lfpost2 = LFPost("something", ":D:D:D:D:D", 2, False)
# lf_db.add_post(lfpost1)
# lf_db.add_post(lfpost2)
# --- end init ---

app.config["STORE_DB"] = store_db
app.config["LF_DB"] = lf_db

# return app


#""" <old>
@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/lostfound", methods=["POST", "GET"])
def lostfound_page():
    lf_db = current_app.config["LF_DB"]
    posts = lf_db.get_all_posts()
    print("\n\n\n", posts, "\n\n\n")    # DEBUGS

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

@app.route("/login", methods=["POST", "GET"])
def login_page():

    return render_template("login.html")    

#</old> """


if __name__ == "__main__":
    # dbinit.initialize(connection_string)
    #app = create_app(app)
    app.run(debug=True)
