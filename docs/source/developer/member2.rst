Parts Implemented by Alperen Yýlmaz
===================================

The selling, question, answer and image relations in the database are implemented and handled by Alperen Yýlmaz.

Database relations:

    .. code-block:: sql

        CREATE TABLE IF NOT EXISTS selling (
	        sellid serial primary key,
   	        itemname varchar(100),
            imageid integer references image(imageid) ON DELETE set default ON UPDATE CASCADE DEFAULT 1,
            seller varchar(10) references users ON DELETE CASCADE ON UPDATE CASCADE,
            iteminfo varchar(500),
	        shortD varchar(50) DEFAULT 'No description.',
	        price integer NOT NULL,
	        sharetime VARCHAR(32)
	    );

	    CREATE TABLE IF NOT EXISTS question (
		    questionid serial primary key,
    		userid varchar(10) references users ON DELETE CASCADE ON UPDATE CASCADE,
	        sellid integer references selling(sellid) ON DELETE CASCADE ON UPDATE CASCADE,
	        body varchar(500),
	        sharetime VARCHAR(32),
	        lastupdate VARCHAR(32),
		    anonymous boolean DEFAULT FALSE,
		    backcolor varchar(16)
	    );

	    CREATE TABLE IF NOT EXISTS answer (
		    answerid serial primary key,
		    userid varchar(10) references users ON DELETE CASCADE ON UPDATE CASCADE,
	        sellid integer references selling(sellid) ON DELETE CASCADE ON UPDATE CASCADE,
	        questionid integer references question(questionid) ON DELETE CASCADE ON UPDATE CASCADE,
	        body varchar(500),
	        sharetime VARCHAR(32),
	        lastupdate VARCHAR(32),
		    anonymous boolean DEFAULT FALSE,
		    backcolor varchar(16)
	    );

Corresponding classes for handling data:

- Selling item:

    .. code-block:: python

        class SellItem:
            def __init__(self, sellid, item_name, price, seller_name, seller_no, n_questions, n_answers, share_time, item_info=None, shortD=None, image=None):
                if(shortD == None):
                    shortD = "No description."
                if(image == None):
                    image = "no image available"

                self.sellid = sellid
                self.item_name = item_name
                self.price = price
                self.seller_name = seller_name
                self.seller_no = seller_no
                self.n_questions = n_questions
                self.n_answers = n_answers
                self.share_time = share_time
                self.item_info = item_info
                self.shortD = shortD
                self.image = image

            def set_nq(n_questions):
                self.n_questions = n_questions

            def set_na(n_answers):
                self.n_answers = n_answers

- Question:

    .. code-block:: python

        class Question:
            def __init__(self, questionid, q_body, user_no, user_name, sellid, color, last_update, share_time, anonymous):

                self.questionid = questionid
                self.q_body = q_body
                self.user_no = user_no
                self.user_name = user_name
                self.sellid = sellid
                self.color = color
                self.last_update = last_update
                self.share_time = share_time
                self.anonymous = anonymous
            
- Answer:

    .. code-block:: python

        class Answer:
            def __init__(self, answerid, questionid, ans_body, user_no, user_name, sellid, color, last_update, share_time, anonymous):

                self.answerid = answerid
                self.questionid = questionid
                self.ans_body = ans_body
                self.user_no = user_no
                self.user_name = user_name
                self.sellid = sellid
                self.color = color
                self.last_update = last_update
                self.share_time = share_time
                self.anonymous = anonymous

Login and Logout
----------------
The login process is handled in the "login_page()" function. After getting a post request that includes the login information, the function hashes the acquired password and checks for validity of the user. If the login information is valid, a session for that user is created.
The logout process is handled in the "logout_page()" function. All this function does is to clear the session.

    .. code-block:: python

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
                session["userid"] = userid

                return redirect("/")

            return render_template("login.html")

    .. code-block:: python

        @app.route("/logout", methods=["POST", "GET"])
        def logout_page():
            session.clear()
            flash("Successfully logged out.", "info")
            return redirect(url_for('home_page'))


Store - Selling Item
--------------------
The table in the main page of the store gets the information from the database. All of the store related tasks are handled in store_database class.

Fetch all selling items:

- sql_getAllSellingInfo:

    .. code-block:: sql

        SELECT selling.sellid, selling.itemname, selling.shortD, selling.iteminfo, selling.price, users.name, users.studentno, image.image, selling.sharetime, count(question.questionid), count(answer.answerid)
        FROM selling left join users ON selling.seller = users.studentno
                    left join image ON selling.imageid = image.imageid
                    left join question ON selling.sellid = question.sellid
                    left join answer ON question.questionid = answer.questionid
                                    AND selling.sellid = answer.sellid
        WHERE (selling.itemname LIKE %(item_name)s
            AND users.name LIKE %(seller)s
            AND selling.price >= %(price_lw)s
            AND selling.price <= %(price_hi)s)
        GROUP BY selling.sellid, selling.itemname, selling.shortD, selling.iteminfo, selling.price, users.name, users.studentno, image.image, selling.sharetime
        ORDER BY selling.sharetime DESC;

- sql_getMaxPrice:

    .. code-block:: sql

        SELECT max(price)
        FROM selling;

If one of the parts of the filter form is left blank, the corresponding part in the sql statement is filled to have no effect on filtering.

    .. code-block:: python

        def get_all_from_db(self, item_name="%", seller_name="%", price_lw=0, price_hi=-1):
            self.selling.clear()

            if item_name != "%":
                item_name = "%" + item_name + "%"

            if seller_name != "%":
                seller_name = "%" + seller_name + "%"

            with dbapi2.connect(self.dsn) as connection:
                cursor = connection.cursor()

                if price_hi == -1:
                    cursor.execute(sql_getMaxPrice)
                    maxPrice = cursor.fetchall()
                    if len(maxPrice) > 0:
                        price_hi = maxPrice[0][0]

                cursor.execute(sql_getAllSellingInfo, {'item_name': item_name, 'seller': seller_name, 'price_lw': price_lw, 'price_hi': price_hi})
                for row in cursor:
                    sellid, item_name, shortD, item_info, price, seller_name, seller_no, image, share_time, n_ques, n_ans = row
                    self.selling[sellid] = SellItem(sellid, item_name, price, seller_name, seller_no, n_ques, n_ans, share_time, item_info=item_info, shortD=shortD, image=image)

                cursor.close()

Update item:

Updating is done via the item page. After the html form to submit the update of item information, the corresponding python statements are used to handle this task.

    .. code-block:: python

        elif request.form.get("form_key") == "item_update":  # logged in
            new_item_name = request.form.get("item_name")
            new_price = request.form.get("price")
            new_item_info = request.form.get("item_info")
            new_shortD = request.form.get("shortD")  # handle empty case!
            update_time = getTimestampString()

            try:
                int(new_price)
            except Exception as e:
                flash("Price must be an integer (TL)", "error")
                return redirect('/store/{}'.format(sellid))

            store_db.update_selling_item(sellid, new_item_name, new_price, new_shortD, new_item_info, update_time)

            return redirect('/store/{}'.format(sellid))

This piece of code uses the update_selling_item function of the store_db object of type store_database

- sql_updateSellingItem:

    .. code-block:: sql

        UPDATE selling
        SET itemname = %(new_item_name)s,
            price = %(new_price)s,
            shortD = %(new_shortD)s,
            iteminfo = %(new_item_info)s,
            sharetime = %(update_time)s
        WHERE (selling.sellid = %(sellid)s);

    .. code-block:: python

        def update_selling_item(self, sellid, new_item_name, new_price, new_shortD, new_item_info, update_time):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_updateSellingItem, {'sellid': sellid, 'new_item_name': new_item_name, 'new_price': new_price, 'new_shortD': new_shortD, 'new_item_info': new_item_info, 'update_time': update_time})

            cursor.close()

Delete item:

Deleting is done via the item page. After the html form to submit the delete command, the corresponding python statements are used to handle this task.

    .. code-block:: python

        elif request.form.get("form_key") == "item_delete":  # logged in
            flash("Post has been deleted successfully.", "info")

            store_db.delete_selling_item(sellid)
            return redirect(url_for('store_page'))

This piece of code uses the delete_selling_item function of the store_db object of type store_database

- sql_deleteSellingItem:

    .. code-block:: sql

        DELETE FROM selling
        WHERE (selling.sellid = %(sellid)s)

    .. code-block:: python

        def delete_selling_item(self, sellid):

            with dbapi2.connect(self.dsn) as connection:
                cursor = connection.cursor()

                cursor.execute(sql_deleteSellingItem, {'sellid': sellid})

                cursor.close()

Store - Question
----------------
All of the question related tasks are done via item page.

Fetch all of the questions and their corresponding answers:

- sql_getAllQuestions:

    .. code-block:: sql

        SELECT question.questionid, question.body, question.userid, users.name, question.backcolor, question.lastupdate, question.sharetime, question.anonymous
        FROM question, users
        WHERE (question.userid = users.studentno
            AND question.sellid = %(sellid)s)
        ORDER BY question.sharetime DESC;

- sql_getAllAnsOfOneQuestion:

    .. code-block:: sql

        SELECT answer.answerid, answer.body, answer.userid, users.name, answer.backcolor, answer.lastupdate, answer.sharetime, answer.anonymous
        FROM answer, users
        WHERE (answer.userid = users.studentno
            AND answer.questionid = %(questionid)s
            AND answer.sellid = %(sellid)s)
        ORDER BY answer.sharetime DESC;

    .. code-block:: python

		def get_all_question_answer_pairs(self, sellid):

			all_questions = []
			with dbapi2.connect(self.dsn) as connection:
				
				cursor = connection.cursor()

				cursor.execute(sql_getAllQuestions, {'sellid': sellid})
				questions = cursor.fetchall()
				for questionid, q_body, q_userid_no, q_user_name, q_color, q_last_update, q_share_time, q_anonymous in questions:
					
					qi_and_all_ans = []

					q_i = Question(questionid, q_body, q_userid_no, q_user_name, sellid, q_color, q_last_update, q_share_time, q_anonymous)
					qi_and_all_ans.append(q_i)

					cursor.execute(sql_getAllAnsOfOneQuestion, {'questionid': questionid, 'sellid': sellid})
					answers = cursor.fetchall()

					ans_of_qi = []
					for answerid, ans_body, ans_userid_no, ans_user_name, ans_color, ans_last_update, ans_share_time, ans_anonymous in answers:
						
						ans_i = Answer(answerid, questionid, ans_body, ans_userid_no, ans_user_name, sellid, ans_color, ans_last_update, ans_share_time, ans_anonymous)
						ans_of_qi.append(ans_i)

					ans_of_qi = tuple(ans_of_qi)
					qi_and_all_ans.append(ans_of_qi)
					qi_and_all_ans = tuple(qi_and_all_ans)
					all_questions.append(qi_and_all_ans)

				cursor.close()

			return all_questions

Inserting a question to the database:

- sql_insertQuestion:

    .. code-block:: sql

        INSERT INTO question (userid, sellid, body, backcolor, lastupdate, sharetime, anonymous) VALUES (
            %(userid_no)s,
            %(sellid)s,
            %(q_body)s,
            %(color)s,
            %(last_update)s,
            %(share_time)s,
            %(anonymous)s
        );

    .. code-block:: python

        def add_question(self, question):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_insertQuestion, {'userid_no': question.user_no, 'sellid': question.sellid, 'q_body': question.q_body, 'color': question.color, 'last_update': question.last_update, 'share_time': question.share_time, 'anonymous': question.anonymous})

            cursor.close()

Update question:

After a question update form is submitted, the following python codeblock is run. The form includes the questionid to identify which question is going to be updated.

    .. code-block:: python

        elif request.form.get("form_key") == "q_update":  # logged in
            new_q_body = request.form.get("q_body")
            questionid = request.form.get("questionid")
            update_time = getTimestampString()

            store_db.update_question(questionid, sellid, new_q_body, update_time)

            return redirect('/store/{}'.format(sellid))

This portion of the code uses the update_question function of the store_db object of type store_database

- sql_updateQuestion:

    .. code-block:: sql

        UPDATE question
        SET body = %(new_q_body)s,
            lastupdate = %(update_time)s
        WHERE (question.sellid = %(sellid)s
            AND question.questionid = %(questionid)s);

    .. code-block:: python

        def update_question(self, questionid, sellid, new_q_body, update_time):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_updateQuestion, {'new_q_body': new_q_body, 'update_time': update_time, 'sellid': sellid, 'questionid': questionid})

            cursor.close()

Delete question:

After a question delete form is submitted, the following python codeblock is run. The form includes the questionid to identify which question is going to be deleted.

    .. code-block:: python

        elif request.form.get("form_key") == "q_delete":  # logged in
            questionid = request.form.get("questionid")

            store_db.delete_question(questionid, sellid)

            flash("Question has been deleted successfully.", "info")
            return redirect('/store/{}'.format(sellid))

This portion of the code uses the delete_question function of the store_db object of type store_database

- sql_deleteQuestion:

    .. code-block:: sql

        DELETE FROM question
        WHERE (question.sellid = %(sellid)s
            AND question.questionid = %(questionid)s);

    .. code-block:: python

        def delete_question(self, questionid, sellid):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_deleteQuestion, {'sellid': sellid, 'questionid': questionid})

            cursor.close()

Store - Answer
--------------
All of the answer related tasks are done via item page.

The fetch process of the answers are done together with the questions as stated above.

Inserting an answer to the database:

- sql_insertAnswer:

    .. code-block:: sql

        INSERT INTO answer (userid, sellid, questionid, body, backcolor, lastupdate, sharetime, anonymous) VALUES (
            %(userid_no)s,
            %(sellid)s,
            %(questionid)s,
            %(ans_body)s,
            %(color)s,
            %(last_update)s,
            %(share_time)s,
            %(anonymous)s
        )

    .. code-block:: python

        def add_answer(self, answer):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_insertAnswer, {'userid_no': answer.user_no, 'sellid': answer.sellid, 'questionid': answer.questionid, 'ans_body': answer.ans_body, 'color': answer.color, 'last_update': answer.last_update, 'share_time': answer.share_time, 'anonymous': answer.anonymous})

            cursor.close()

Update answer:

After a answer update form is submitted, the following python codeblock is run. The form includes the questionid and answerid to identify which answer is going to be updated.

    .. code-block:: python

        elif request.form.get("form_key") == "ans_update":
            new_ans_body = request.form.get("ans_body")
            answerid = request.form.get("answerid")
            questionid = request.form.get("questionid")
            update_time = getTimestampString()

            store_db.update_answer(answerid, questionid, sellid, new_ans_body, update_time)
            return redirect('/store/{}'.format(sellid))

This portion of the code uses the update_answer function of the store_db object of type store_database

- sql_updateAnswer:

    .. code-block:: sql

        UPDATE answer
        SET body = %(new_ans_body)s,
            lastupdate = %(update_time)s
        WHERE (answer.sellid = %(sellid)s
            AND answer.questionid = %(questionid)s
            AND answer.answerid = %(answerid)s);

    .. code-block:: python

        def update_answer(self, answerid, questionid, sellid, new_ans_body, update_time):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_updateAnswer, {'new_ans_body': new_ans_body, 'sellid': sellid, 'questionid': questionid, 'answerid': answerid})

            cursor.close()

Delete question:

After a answer delete form is submitted, the following python codeblock is run. The form includes the questionid and answerid to identify which answer is going to be deleted.

    .. code-block:: python

        elif request.form.get("form_key") == "ans_delete":  # logged in
            answerid = request.form.get("answerid")
            questionid = request.form.get("questionid")

            store_db.delete_answer(answerid, questionid, sellid)

            flash("Answer has been deleted successfully.", "info")
            return redirect('/store/{}'.format(sellid))

This portion of the code uses the delete_answer function of the store_db object of type store_database

- sql_deleteAnswer:

    .. code-block:: sql

        DELETE FROM answer
        WHERE (answer.sellid = %(sellid)s
            AND answer.questionid = %(questionid)s
            AND answer.answerid = %(answerid)s);

    .. code-block:: python

        def delete_answer(self, answerid, questionid, sellid):

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_deleteAnswer, {'sellid': sellid, 'questionid': questionid, 'answerid': answerid})

            cursor.close()

the end
