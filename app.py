from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import os

app = Flask(__name__)

DATA_FILE = "guestbook.json"


def read_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_entries(entries):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    entries = read_entries()
    # Senaste inläggen först
    entries.reverse()
    return render_template("index.html", entries=entries)


@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        entries = read_entries()
        new_post = {
            "name": request.form.get("name", "Anonym"),
            "email": request.form.get("email", ""),
            "message": request.form.get("message", ""),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        entries.append(new_post)
        save_entries(entries)
        return redirect(url_for("index"))
    return render_template("form.html")


if __name__ == "__main__":
    app.run(debug=True)
