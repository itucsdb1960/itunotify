from sell_item import SellItem
import psycopg2 as dbapi2
from sell_item import SellItem


class StoreDatabase:
    def __init__(self):
        self.selling = {}
        self.last_sellid = 0

        file = open(r"/database_connection", "r")
        self.dsn = file.read()

        sql_getAllSelling = """SELECT selling.sellid, item.name, selling.shortD, selling.price, user.name, image.image
								FROM selling, user, item, image
								WHERE (selling.itemid = item.itemid
										AND selling.seller = user.userid
										AND selling.imageid = image.imageid)
								ORDER BY selling.sellid"""

        sql_getNoQuestions = """SELECT selling.sellid, count(question.questionid)
								FROM selling, question
								WHERE (selling.sellid = question.sellid)
								GROUP BY selling.sellid
								ORDER BY selling.sellid;"""

        sql_getNoAnswers = """SELECT selling.sellid, count(answer.answerid)
								FROM selling, answer
								WHERE (selling.sellid = answer.sellid)
								GROUP BY selling.sellid
								ORDER BY selling.sellid;"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_getAllSelling)
            for row in cursor:
                sellid, item_name, shortD, price, seller, image = row
                self.selling[sellid] = SellItem(item_name, price, seller, 0, 0, shortD=shortD, image=image)
                self.last_sellid = max(sellid, self.last_sellid)

            cursor.execute(sql_getNoQuestions)
            for row in cursor:
                sellid, n_questions = row
                self.selling[sellid].set_nq(n_questions)

            cursor.execute(sql_getNoAnswers)
            for row in cursor:
                sellid, n_answers = row
                self.selling[sellid].set_nq(n_answers)

            cursor.close()

        # normally get selling items from the sql database!

    def add_selling_item(self, sellItem):
        self.last_sellid += 1
        self.selling[self.last_sellid] = sellItem

        itemid = 0
        userid = 0
        imageid = 0

        sql_insertSelling = """INSERT INTO selling (itemid, imageid, seller, shortD, price) VALUES(
									%(itemid)s,
									%(imageid)s,
									%(seller)s,
									%(shortD)s,
									%(price)s
								);"""

        # if item_name and image doesnt exist, create
        sql_itemExists = """SELECT item.itemid, item.name
        					FROM item
        					WHERE (item.name = %(item_name)s);"""

        sql_insertItem = """INSERT INTO item (name) VALUES(
								%(item_name)s
							);"""

            sql_imageExists = """SELECT image.imageid, image.image
        						FROM image
        						WHERE (image.image = %(image)s);"""

        sql_insertImage = """INSERT INTO image (image) VALUES(
								%(image)s
							);"""

        with dbapi2.connect(self.dsn) as connection:
            cursor = connection.cursor()

            cursor.execute(sql_itemExists, {'item_name': sellItem.item_name})
            itemExist = cursor.fetchall()
            if len(itemExist) == 0:
                # create item
                cursor.execute(sql_insertItem, {'item_name': sellItem.item_name})
                cursor.execute(sql_itemExists, {'item_name': sellItem.item_name})
                new_item = cursor.fetchall()
                itemid = new_item[0][0]
            else:
                itemid = itemExist[0][0]

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

                cursor.execute(sql_insertSelling, {'itemid': itemid, 'imageid': imageid, 'seller': userid, 'shortD': sellItem.shortD, 'price': sellItem.price})

            cursor.close()

        # handle sql database!

    def delete_selling_item(self, sellid):
        if sellid in self.selling:
            del self.selling[sellid]

        # handle sql database!

    def get_selling_item(self, sellid):
        sellItem = self.selling.get(sellid)
        if sellItem is None:
            return None
        sellItem_new = SellItem(sellItem.item_name, sellItem.price, sellItem.seller, sellItem.n_questions, sellItem.n_answers, shortD=sellItem.shortD, image=sellItem.image)
        return sellItem_new

    def get_all_selling_items(self):
        sellingItems = []
        for sellid, sellItem in self.selling.items():
            sellItem_new = SellItem(sellItem.item_name, sellItem.price, sellItem.seller, sellItem.n_questions, sellItem.n_answers, shortD=sellItem.shortD, image=sellItem.image)
            sellingItems.append((sellid, sellItem_new))
        return sellingItems
