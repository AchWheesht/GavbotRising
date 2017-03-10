from flask import Flask, render_template, request, make_response, redirect, session
import sys
import re
import jinja2
import page_manager
import os
import json

app = Flask(__name__)
app.jinja_env.autoescape = False
current_bots = {}

@app.route("/")
def index():
    if 'username' in session:
        return render_template("index.html", gavbot=current_bots[session['username']])
    else:
        return render_template("index_null.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        current_bots[session["username"]] = page_manager.Gavbot(session["username"])
        return redirect("/")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

@app.route("/reset")
def reset():
    current_bots[session['username']].reset_gavbot()
    return redirect("/")

@app.route('/page/', defaults={'path': ''})
@app.route('/page/<path:path>')
def move_page(path):
    if 'username' in session:
        current_bots[session['username']].update_page(path)
        return redirect("/")
    else:
        return redirect("/")

if __name__ == "__main__":

    app.secret_key = os.urandom(32)

    bind = "127.0.0.1"

    if len(sys.argv) == 2:
        bind = sys.argv[1]

    app.run(host=bind)
