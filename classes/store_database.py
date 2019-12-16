from classes.sell_item import SellItem
from classes.Q_and_A import Question, Answer
import psycopg2 as dbapi2


class StoreDatabase:
    def __init__(self):
        self.selling = {}

        file = open(r"heroku_db_url.txt", "r")
        self.dsn = file.read()
        #self.dsn = "dbname='postgres' user='postgres' password='postgrepass' host='localhost' port=5432"

        # self.get_all_from_db()

        # normally get selling items from the sql database!

    def get_all_from_db(self, item_name="%", seller_name="%", price_lw=0, price_hi=-1):
        self.selling.clear()

        if item_name != "%":
            item_name = "%" + item_name + "%"

        if seller_name != "%":
            seller_name = "%" + seller_name + "%"

        sql_getAllSellingInfo = """SELECT selling.sellid, selling.itemname, selling.shortD, selling.iteminfo, selling.price, users.name, users.studentno, image.image, selling.sharetime, count(question.questionid), count(answer.answerid)
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
                                    ORDER BY selling.sharetime DESC;"""

        sql_getMaxPrice = """SELECT max(price)
                                FROM selling;"""

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

    def add_selling_item(self, sellItem):

        imageid = 0

        sql_insertSelling = """INSERT INTO selling (itemname, imageid, seller, shortD, price, sharetime) VALUES(
                                    %(item_name)s,
                                    %(imageid)s,
                                    %(seller_no)s,
                                    %(shortD)s,
                                    %(price)s,
                                    %(share_time)s
                                );"""

        sql_imageExists = """SELECT image.imageid, image.image
                                FROM image
                                WHERE (image.image = %(image)s);"""

        sql_insertImage = """INSERT INTO image (image) VALUES(
                                %(image)s
                            );"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_imageExists, {'image': sellItem.image})
            imageExist = cursor.fetchall()
            if len(imageExist) == 0:
                # create image
                cursor.execute(sql_insertImage, {'image': sellItem.image})
                cursor.execute(sql_imageExists, {'image': sellItem.image})
                new_image = cursor.fetchall()
                imageid = new_image[0][0]
            else:
                imageid = imageExist[0][0]

            # set userid correctly!

            cursor.execute(sql_insertSelling, {'item_name': sellItem.item_name, 'imageid': imageid, 'seller_no': sellItem.seller_no, 'shortD': sellItem.shortD, 'price': sellItem.price, 'share_time': sellItem.share_time})

            cursor.close()

        self.get_all_from_db()

        # handle sql database!

    def update_selling_item(self, sellid, new_item_name, new_price, new_shortD, new_item_info, update_time):

        sql_updateSellingItem = """UPDATE selling
                                    SET itemname = %(new_item_name)s,
                                        price = %(new_price)s,
                                        shortD = %(new_shortD)s,
                                        iteminfo = %(new_item_info)s,
                                        sharetime = %(update_time)s
                                    WHERE (selling.sellid = %(sellid)s);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_updateSellingItem, {'sellid': sellid, 'new_item_name': new_item_name, 'new_price': new_price, 'new_shortD': new_shortD, 'new_item_info': new_item_info, 'update_time': update_time})

            cursor.close()

    def delete_selling_item(self, sellid):

        sql_deleteSellingItem = """DELETE FROM selling
                                    WHERE (selling.sellid = %(sellid)s);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_deleteSellingItem, {'sellid': sellid})

            cursor.close()

        # handle sql database!

    def get_selling_item(self, sellid):
        self.get_all_from_db()
        sellItem = self.selling.get(sellid)

        if sellItem is None:
            return None

        sellItem_new = SellItem(sellItem.sellid, sellItem.item_name, sellItem.price, sellItem.seller_name, sellItem.seller_no, sellItem.n_questions, sellItem.n_answers, sellItem.share_time, item_info=sellItem.item_info, shortD=sellItem.shortD, image=sellItem.image)
        return sellItem_new

    def add_question(self, question):

        sql_insertQuestion = """INSERT INTO question (userid, sellid, body, backcolor, lastupdate, sharetime, anonymous) VALUES (
                                %(userid_no)s,
                                %(sellid)s,
                                %(q_body)s,
                                %(color)s,
                                %(last_update)s,
                                %(share_time)s,
                                %(anonymous)s
                            );"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_insertQuestion, {'userid_no': question.user_no, 'sellid': question.sellid, 'q_body': question.q_body, 'color': question.color, 'last_update': question.last_update, 'share_time': question.share_time, 'anonymous': question.anonymous})

            cursor.close()

    def update_question(self, questionid, sellid, new_q_body, update_time):

        sql_updateQuestion = """UPDATE question
                                SET body = %(new_q_body)s,
                                    lastupdate = %(update_time)s
                                WHERE (question.sellid = %(sellid)s
                                    AND question.questionid = %(questionid)s);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_updateQuestion, {'new_q_body': new_q_body, 'update_time': update_time, 'sellid': sellid, 'questionid': questionid})

            cursor.close()

    def delete_question(self, questionid, sellid):

        sql_deleteQuestion = """DELETE FROM question
                                WHERE (question.sellid = %(sellid)s
                                    AND question.questionid = %(questionid)s);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_deleteQuestion, {'sellid': sellid, 'questionid': questionid})

            cursor.close()

    def add_answer(self, answer):

        sql_insertAnswer = """INSERT INTO answer (userid, sellid, questionid, body, backcolor, lastupdate, sharetime, anonymous) VALUES (
                                %(userid_no)s,
                                %(sellid)s,
                                %(questionid)s,
                                %(ans_body)s,
                                %(color)s,
                                %(last_update)s,
                                %(share_time)s,
                                %(anonymous)s
                            );"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_insertAnswer, {'userid_no': answer.user_no, 'sellid': answer.sellid, 'questionid': answer.questionid, 'ans_body': answer.ans_body, 'color': answer.color, 'last_update': answer.last_update, 'share_time': answer.share_time, 'anonymous': answer.anonymous})

            cursor.close()

    def update_answer(self, answerid, questionid, sellid, new_ans_body, update_time):

        sql_updateAnswer = """UPDATE answer
                                SET body = %(new_ans_body)s,
                                    lastupdate = %(update_time)s
                                WHERE (answer.sellid = %(sellid)s
                                    AND answer.questionid = %(questionid)s
                                    AND answer.answerid = %(answerid)s);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_updateAnswer, {'new_ans_body': new_ans_body, 'sellid': sellid, 'questionid': questionid, 'answerid': answerid})

            cursor.close()

    def delete_answer(self, answerid, questionid, sellid):

        sql_deleteAnswer = """DELETE FROM answer
                                WHERE (answer.sellid = %(sellid)s
                                    AND answer.questionid = %(questionid)s
                                    AND answer.answerid = %(answerid)s);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_deleteAnswer, {'sellid': sellid, 'questionid': questionid, 'answerid': answerid})

            cursor.close()

    def get_all_question_answer_pairs(self, sellid):

        # question.sellid :: already known
        sql_getAllQuestions = """SELECT question.questionid, question.body, question.userid, users.name, question.backcolor, question.lastupdate, question.sharetime, question.anonymous
                            FROM question, users
                            WHERE (question.userid = users.studentno
                                AND question.sellid = %(sellid)s)
                            ORDER BY question.sharetime DESC;"""

        # answer.questionid, answer.sellid :: already known
        sql_getAllAnsOfOneQuestion = """SELECT answer.answerid, answer.body, answer.userid, users.name, answer.backcolor, answer.lastupdate, answer.sharetime, answer.anonymous
                                        FROM answer, users
                                        WHERE (answer.userid = users.studentno
                                            AND answer.questionid = %(questionid)s
                                            AND answer.sellid = %(sellid)s)
                                        ORDER BY answer.sharetime DESC;"""

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

    def get_all_selling_items(self, item_name="%", seller_name="%", price_lw=0, price_hi=-1):
        if item_name == '' or item_name == None:
            item_name = "%"
        if seller_name == '' or seller_name == None:
            seller_name = "%"
        if price_lw == '' or price_lw == None:
            price_lw = 0
        if price_hi == '' or price_hi == None:
            price_hi = -1

        self.get_all_from_db(item_name=item_name, seller_name=seller_name, price_lw=price_lw, price_hi=price_hi)

        sellingItems = []
        for sellid, sellItem in self.selling.items():
            sellItem_new = SellItem(sellItem.sellid, sellItem.item_name, sellItem.price, sellItem.seller_name, sellItem.seller_no, sellItem.n_questions, sellItem.n_answers, sellItem.share_time, item_info=sellItem.item_info, shortD=sellItem.shortD, image=sellItem.image)
            sellingItems.append((sellid, sellItem_new))
        return sellingItems
