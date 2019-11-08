from flask import Flask, current_app, render_template
#import views
from store_database import StoreDatabase
from sell_item import SellItem
import dbinit
#import psycopg2

# <old> app = Flask(__name__)
connection_string = "dbname='postgres' user='postgres' password='' host='localhost' port=5432"

app = Flask(__name__)


def create_app(app):
    #app = Flask(__name__)

    #app.add_url_rule("/", view_func=views.home_page)
    #app.add_url_rule("/lostfound", view_func=views.lostfound_page, methods=["POST", "GET"])
    #app.add_url_rule("/store", view_func=views.store_page, endpoint='store_page', methods=["POST", "GET"])

    store_db = StoreDatabase()
    sellItem1 = SellItem("fridge", 100, "alp", 3, 6, shortD="buy please", image="fridge image")
    sellItem2 = SellItem("pen", 3343, "eren", 5, 3)
    store_db.add_selling_item(sellItem1)
    store_db.add_selling_item(sellItem2)
    app.config["store_db"] = store_db

    return app


#""" <old>
@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/lostfound", methods=["POST", "GET"])
def lostfound_page():
    return render_template("lost_and_found.html")


@app.route("/store", methods=["POST", "GET"])
def store_page():
    store_db = current_app.config["store_db"]
    selling_items = store_db.get_all_selling_items()
    return render_template("store.html", selling_items=sorted(selling_items))
#</old> """


if __name__ == "__main__":
    app = create_app(app)
    app.run(debug=True)
    # dbinit.initialize(connection_string)
