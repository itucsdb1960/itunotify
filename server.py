from flask import Flask, render_template
import views
import dbinit
#import psycopg2

# <old> app = Flask(__name__)
connection_string = "dbname='postgres' user='postgres' password='' host='localhost' port=5432"


def create_app():
    app = Flask(__name__)

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/lostfound", view_func=views.lostfound_page, methods=["POST", "GET"])
    app.add_url_rule("/store", view_func=views.store_page, endpoint='store_page', methods=["POST", "GET"])

    return app


""" <old>
@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/lostfound", methods=["POST", "GET"])
def lostfound_page():
    return render_template("lost_and_found.html")


@app.route("/store", endpoint='store_page', methods=["POST", "GET"])
def store_page():
    return render_template("store.html")
</old> """

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
    # dbinit.initialize(connection_string)
