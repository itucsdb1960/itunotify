from flask import Flask, current_app, render_template, request, session, flash, redirect, url_for

# Importing custom classes
from classes.store_database import StoreDatabase
from classes.sell_item import SellItem
from classes.Q_and_A import Question, Answer
from classes.lostfound_database import LFPost, LFResponse, LFDatabase

from classes.user_database import User, UserDatabase

import dbinit

import psycopg2 as dbapi2
from hashlib import sha256  # hashing passwords

import random  # for tests
from datetime import datetime   # obtain sharing time on form post


def getTimestampString():
    return " ~ ".join(str(datetime.now()).split(" ")).replace("-", "/")[:-7]    # might be a little complicated :)


connection_string = "dbname='postgres' user='postgres' password='postgrepass' host='localhost' port=5432"

app = Flask(__name__)
app.secret_key = b'dsfghj+*/-8lo98k'


store_db = StoreDatabase()
lf_db = LFDatabase()
user_db = UserDatabase()


app.config["STORE_DB"] = store_db
app.config["LF_DB"] = lf_db
app.config["USER_DB"] = user_db

#
# HOME PAGE VIEW FUNCTION
#


@app.route("/")
def home_page():
    return render_template("index.html")


#
# LOST ITEM PAGES VIEW FUNCTIONS
#
@app.route("/lostfound", methods=["POST", "GET"])
def lostfound_page():
    lf_db = current_app.config["LF_DB"]
    posts = lf_db.get_all_posts()

    if request.method == "POST":
        form_name = request.form.get("form_key")

        # new post created from /lostfound
        if form_name == "new_post":
            if not session.get("is_loggedin", False):   # if not logged in, log in :)
                flash("You must login first to do that!", "error")
                return redirect("/login")

            title = request.form.get("title")
            if len(title) > 32:
                title = title[:29] + "..."
            description = request.form.get("description")
            # userid = session["user_dict"]["userid"] # The user object who is logged in is stored in session["user"]
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

        # Delete Post button is activated in /lostfound/<int:postid>
        elif form_name == "delete_post":
            postowner_userid = request.form.get("userid")
            postid = request.form.get("postid")

            # user must be post owner to be able to delete. if not, print error and redirect to same post's page
            if not session.get("userid") == postowner_userid:
                flash("You do not have authentication to do that!", "error")
                return redirect("/lostfound/{}".format(postid))

            lf_db.delete_post(postid)
            flash("Post is deleted successfully.", "info")
            return redirect("/lostfound")

    return render_template("lost_and_found.html", posts=posts)


@app.route("/lostfound/<int:postid>", methods=["POST", "GET"])
def lfpost_page(postid):
    lf_db = current_app.config["LF_DB"]
    post, extra = lf_db.get_post(postid)
    responses = lf_db.get_all_responses_for_post(postid)

    if request.method == "POST":
        form_name = request.form.get("form_key")

        # new response created from same page
        if form_name == "new_response":
            if not session.get("is_loggedin", False):   # if not logged in, log in :)
                flash("You must login first to do that!", "error")
                return redirect("/login")

            response_message = request.form.get("response")
            anonymous = request.form.get("hide_name")
            userid = "0000000000" if anonymous else session["userid"]
            timestamp = getTimestampString()

            lfresponse = LFResponse(postid, response_message, userid, timestamp)    # not passing order attribute, default=0
            lf_db.add_response(lfresponse)
            responses = lf_db.get_all_responses_for_post(postid)
            return redirect("/lostfound/{}".format(postid))

        elif form_name == "delete_response":
            respowner_userid = request.form.get("userid")
            respid = request.form.get("respid")
            postid = request.form.get("postid")

            # user must be response owner to be able to delete. if not, print error and redirect to same post's page
            if not session.get("userid") == respowner_userid:
                flash("You do not have authentication to do that!", "error")
                return redirect("/lostfound/{}".format(postid))

            lf_db.delete_response(respid)
            flash("Message is deleted successfully.", "info")
            return redirect("/lostfound/{}".format(postid))

        elif form_name == "update_response":
            respowner_userid = request.form.get("userid")
            if not session.get("userid") == respowner_userid:
                flash("You do not have authentication to do that!", "error")
                return redirect("/lostfound/{}".format(postid))

            respid = request.form.get("respid")
            new_message = request.form.get("new_response")
            lf_db.update_response(new_message, respid)
            flash("Response is updated successfully.", "info")
            return redirect("/lostfound/{}".format(postid))

        elif form_name == "update_post":
            postowner_userid = request.form.get("userid")
            if not session.get("userid") == postowner_userid:
                flash("You do not have authentication to do that!", "error")
                return redirect("/lostfound/{}".format(postid))

            # postid = request.form.get("postid")    # postid is already known
            new_description = request.form.get("new_description")
            lf_db.update_post(new_description, postid)
            flash("Post description is updated successfully.", "info")
            return redirect("/lostfound/{}".format(postid))

    return render_template("lfpost.html", post=post, extra=extra, responses=responses)


#
# STORE PAGES VIEW FUNCTIONS
#
@app.route("/store", endpoint='store_page', methods=["POST", "GET"])
def store_page():
    store_db = current_app.config["STORE_DB"]
    user_db = current_app.config["USER_DB"]

    if request.method == "POST":
        if request.form.get("form_key") == "sell":
            # sell form submitted
            if not ("is_loggedin" in session) or (not session["is_loggedin"]):
                # not logged in -> cannot sell item
                # redirect to login
                return redirect(url_for('login_page'))

            item_name = request.form.get("item_name")
            price = request.form.get("price")
            seller_name = session["username"]
            seller_no = session["userid"]
            share_time = getTimestampString()
            shortD = request.form.get("shortD")  # handle empty case!
            image = request.form.get("image")  # handle empty case!

            sellItem = SellItem(-1, item_name, price, seller_name, seller_no, 0, 0, share_time, shortD=shortD, image=image)
            store_db.add_selling_item(sellItem)
            selling_items = store_db.get_all_selling_items()
            filter_items = [('', '', '', '')]
            return redirect(url_for('store_page'))
            # return render_template("store.html", selling_items=selling_items, filter_items=filter_items)

        elif request.form.get("form_key") == "login":
            # login form submitted
            return redirect(url_for('login_page'))

        elif request.form.get("form_key") == "filter":
            # filter form submitted
            item_name = request.form.get("item_name")
            price_lw = request.form.get("price_lw")
            price_hi = request.form.get("price_hi")
            seller_name = request.form.get("seller_name")

            if request.form.get("drop_filter"):
                selling_items = store_db.get_all_selling_items()
                filter_items = [('', '', '', '')]
            else:
                selling_items = store_db.get_all_selling_items(item_name=item_name, seller_name=seller_name, price_lw=price_lw, price_hi=price_hi)
                filter_items = [(item_name, seller_name, price_lw, price_hi)]

            return render_template("store.html", selling_items=selling_items, filter_items=filter_items)

    selling_items = store_db.get_all_selling_items()
    filter_items = [('', '', '', '')]
    return render_template("store.html", selling_items=selling_items, filter_items=filter_items)


@app.route("/store/<int:sellid>", methods=["POST", "GET"])
def storePost_page(sellid):
    store_db = current_app.config["STORE_DB"]
    user_db = current_app.config["USER_DB"]

    if request.method == "POST":
        if request.form.get("form_key") == "login":
            return redirect(url_for('login_page'))

        elif request.form.get("form_key") == "item_delete":  # logged in
            flash("Post has been deleted successfully.", "info")

            store_db.delete_selling_item(sellid)
            return redirect(url_for('store_page'))

        elif request.form.get("form_key") == "item_update":  # logged in
            new_item_name = request.form.get("item_name")
            new_price = request.form.get("price")
            new_item_info = request.form.get("item_info")
            new_shortD = request.form.get("shortD")  # handle empty case!
            update_time = getTimestampString()

            store_db.update_selling_item(sellid, new_item_name, new_price, new_shortD, new_item_info, update_time)

            return redirect('/store/{}'.format(sellid))

        elif request.form.get("form_key") == "ask_question":  # logged in
            q_body = request.form.get("q_body")
            userid_no = session["userid"]
            user_name = session["username"]
            share_time = getTimestampString()

            question = Question(-1, q_body, userid_no, user_name, sellid, share_time)
            store_db.add_question(question)

            return redirect('/store/{}'.format(sellid))

        elif request.form.get("form_key") == "q_update":  # logged in
            new_q_body = request.form.get("q_body")
            questionid = request.form.get("questionid")

            store_db.update_question(questionid, sellid, new_q_body)

            return redirect('/store/{}'.format(sellid))

        elif request.form.get("form_key") == "q_delete":  # logged in
            questionid = request.form.get("questionid")

            store_db.delete_question(questionid, sellid)

            flash("Question has been deleted successfully.", "info")
            return redirect('/store/{}'.format(sellid))

        elif request.form.get("form_key") == "answer":  # logged in
            ans_body = request.form.get("ans_body")
            questionid = request.form.get("questionid")
            userid_no = session["userid"]
            user_name = session["username"]
            share_time = getTimestampString()

            answer = Answer(-1, questionid, ans_body, userid_no, user_name, sellid, share_time)
            store_db.add_answer(answer)
            return redirect('/store/{}'.format(sellid))

        elif request.form.get("form_key") == "ans_update":
            new_ans_body = request.form.get("ans_body")
            answerid = request.form.get("answerid")
            questionid = request.form.get("questionid")

            store_db.update_answer(answerid, questionid, sellid, new_ans_body)
            return redirect('/store/{}'.format(sellid))

        elif request.form.get("form_key") == "ans_delete":  # logged in
            answerid = request.form.get("answerid")
            questionid = request.form.get("questionid")

            store_db.delete_answer(answerid, questionid, sellid)

            flash("Answer has been deleted successfully.", "info")
            return redirect('/store/{}'.format(sellid))

    sellItem = store_db.get_selling_item(sellid)
    questions = store_db.get_all_question_answer_pairs(sellid)

    return render_template("storePost.html", sellItem=sellItem, questions=questions)


@app.route("/courses", methods=["POST", "GET"])
def courses():
    return render_template("courses.html")

#
# LOGIN - LOGOUT - REGISTER FUNCTIONS
#


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

        if  not (4 <= len(user_studentno) <= 10):
            flash("ID must be between 4 and 10 characters long.", "error")
            return redirect(url_for('register_page'))

        if user_name.lower() == "admin" :
            flash("This name is restricted. Please use your real name.", "error")
            return redirect(url_for('register_page'))

        if  not (len(user_password) > 6):
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for('register_page'))    

        if(password_check != user_password):
            # passwords dont match
            flash("Entered passwords do not match", "error")
            return redirect(url_for('register_page'))

        user_password_hash = sha256(user_password.encode()).hexdigest()
        user = User(user_studentno, user_name, user_department, user_grade, user_password_hash)

        user_db.register_user(user)

        return redirect(url_for('home_page'))

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login_page():
    if session.get("is_loggedin", False):
        flash("You are already logged in as {}.".format(session.get("username")), "warning")
        return redirect("/")

    print("\n\n\n", session, "\n\n\n")    # DEBUG
    user_db = current_app.config["USER_DB"]

    if request.method == "POST":
        userid = request.form.get("userid")
        user = user_db.get_user_by_userid(userid)
        if user == None:
            print("NO USER")
            flash("Invalid ID. Are you registered?", "error")
            return redirect("/login")

        password = request.form.get("password")

        hashed_password = sha256(password.encode()).hexdigest()
        print("\n\n\n", password, hashed_password, user.password_hash, "\n\n\n")

        if hashed_password != user.password_hash:
            print("WRONG PASS")
            flash("Incorrect password. Try again or Register.", "error")
            return redirect("/login")

        flash("Successfully logged in as {}".format(user.name), "info")
        session["username"] = user.name
        session["is_loggedin"] = True
        # session["user_dict"] = vars(user)   # save user obj in session (?)
        session["userid"] = userid

        return redirect("/")

    return render_template("login.html")


@app.route("/logout", methods=["POST", "GET"])
def logout_page():
    session.clear()
    flash("Successfully logged out.", "info")
    return redirect(url_for('home_page'))


@app.route("/profile/<string:userid>", methods=["POST", "GET"])
def profile(userid):
    user_db = current_app.config["USER_DB"]
    userobj = user_db.get_user_by_userid(userid)

    if request.method == "POST":
        if request.form.get("form_key") == "update_user_attributes":
            new_name = request.form.get("user_newname")
            new_depart = request.form.get("user_newdepartment")
            new_grade = request.form.get("user_newgrade")
            userobj.name = userobj.name if new_name == "" else new_name
            userobj.department = userobj.department if new_depart == "" else new_depart
            userobj.grade = userobj.grade if new_grade == "" else new_grade

            user_db.update_user_attrs(userobj)
            session["username"] = userobj.name
            return redirect("/profile/{}".format(userid))

        elif request.form.get("form_key") == "update_user_password":
            curr_pass = request.form.get("curr_pass")
            curr_pass_hash = sha256(curr_pass.encode()).hexdigest()
            if curr_pass_hash != userobj.password_hash:
                flash("Incorrect current password.", "warning")
                return redirect("/profile/{}".format(userid))

            new_pass1 = request.form.get("new_pass1")
            new_pass2 = request.form.get("new_pass2")
            if new_pass1 != new_pass2:
                flash("New passwords do not match.", "warning")
                return redirect("/profile/{}".format(userid))

            new_pass_hash = sha256(new_pass1.encode()).hexdigest()
            user_db.update_user_password(new_pass_hash, userid)
            flash("Your password is updated successfully.", "info")
            return redirect("/profile/{}".format(userid))

        elif request.form.get("form_key") == "delete_user":
            studentno = request.form.get("studentno")
            name = request.form.get("name")
            password = request.form.get("password")
            hashed_password = sha256(password.encode()).hexdigest()

            if studentno != userobj.studentno or name != userobj.name or hashed_password != userobj.password_hash:
                flash("Invalid Credentials, Account is not deleted.", "warning")
                return redirect("/profile/{}".format(userid))

            user_db.delete_user(userid)
            flash("Account with ID {} is successfully deleted.".format(userobj.studentno), "info")
            session.clear()
            return redirect("/")

    return render_template("profile.html", userobj=userobj)


if __name__ == "__main__":
    # dbinit.initialize(connection_string)
    # app = create_app(app)
    app.run(debug=True)
