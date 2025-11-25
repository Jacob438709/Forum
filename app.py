from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "supersecretkey" # Change to a secure value


# ----- MySQL-anslutning -----
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="forum_db"
    )


# ----- Startsida -----
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))


    db = get_connection()
    cursor = db.cursor(dictionary=True)


    cursor.execute("SELECT * FROM forum ORDER BY time DESC")
    entries = cursor.fetchall()


    cursor.close()
    db.close()


    return render_template("index.html", entries=entries, username=session.get("username"))


# ----- Nytt inlägg -----
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if "user_id" not in session:
        return redirect(url_for("login"))


    if request.method == "POST":
        name = session.get("username")
        email = session.get("email")
        message = request.form.get("message", "")


        db = get_connection()
        cursor = db.cursor()


        return redirect(url_for("login"))

    return render_template("register.html")


# ----- Login -----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]


        db = get_connection()
        cursor = db.cursor(dictionary=True)


        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()


        cursor.close()
        db.close()


        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            return redirect(url_for("index"))
        else:
            return "Fel användarnamn eller lösenord" # replace later with proper template

    return render_template("login.html")


# ----- Logout -----
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----- Registrering -----
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_pw = generate_password_hash(password)

        db = get_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_pw)
        )

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("login"))

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
