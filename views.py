from flask import Flask, render_template


def home_page():
    return render_template("index.html")


def lostfound_page():
    return render_template("lost_and_found.html")


def store_page():
    return render_template("store.html")
