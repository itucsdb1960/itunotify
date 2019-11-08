from flask import Flask, current_app, render_template


def home_page():
    return render_template("index.html")


def lostfound_page():
    return render_template("lost_and_found.html")


def store_page():
    store_db = current_app.config["store_db"]
    selling_items = store_db.get_all_selling_items()
    return render_template("store.html", selling_items=sorted(selling_items))
