from flask import Flask, render_template
import dbinit
#import psycopg2

app = Flask(__name__)
connection_string = "dbname='postgres' user='postgres' password='' host='localhost' port=5432"


@app.route("/")
def home_page():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
    dbinit.initialize(connection_string)
