from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# ----- MySQL-anslutning -----
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # standard i XAMPP
        password="",       # lämna tomt om du inte satt ett lösenord
        database="guestbook_db"
    )

# ----- Visa inlägg -----
@app.route("/")
def index():
    db = get_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM guestbook ORDER BY time DESC")
    entries = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("index.html", entries=entries)

# ----- Nytt inlägg -----
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        name = request.form.get("name", "Anonym")
        email = request.form.get("email", "")
        message = request.form.get("message", "")

        db = get_connection()
        cursor = db.cursor()

        sql = "INSERT INTO guestbook (name, email, message) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, email, message))

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("index"))

    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
