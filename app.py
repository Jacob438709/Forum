from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "supersecretkey"


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

    cursor.execute("SELECT t.id, t.title, u.username AS creator "
                   "FROM threads t JOIN users u ON t.created_by = u.id "
                   "ORDER BY t.created_at DESC")
    threads = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("threads.html", threads=threads)

# ----- Se trådar -----
@app.route("/threads")
def threads_redirect():
    return redirect(url_for("index"))

# ----- Skapa ny tråd -----
@app.route("/threads/new", methods=["GET", "POST"])
def new_thread():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        user_id = session["user_id"]

        db = get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO threads (title, created_by) VALUES (%s, %s)", (title, user_id))
        db.commit()
        thread_id = cursor.lastrowid
        cursor.close()
        db.close()

        return redirect(url_for("view_thread", thread_id=thread_id))

    return render_template("new_thread.html")
# ----- Visa allt i tråd -----
@app.route("/threads/<int:thread_id>", methods=["GET", "POST"])
def view_thread(thread_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    # Hämta trådens info
    cursor.execute("SELECT t.id, t.title, u.username AS creator FROM threads t JOIN users u ON t.created_by = u.id WHERE t.id=%s", (thread_id,))
    thread = cursor.fetchone()

    # Hämta inlägg
    cursor.execute("SELECT f.id, f.name, f.email, f.message, f.time FROM forum f WHERE f.thread_id=%s ORDER BY f.time ASC", (thread_id,))
    posts = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("thread.html", thread=thread, posts=posts)

# ----- Nytt inlägg i tråd -----
@app.route("/threads/<int:thread_id>/new", methods=["POST"])
def new_post(thread_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    message = request.form["message"]
    name = session["username"]
    email = session["email"]

    db = get_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO forum (name, email, message, thread_id) VALUES (%s, %s, %s, %s)", (name, email, message, thread_id))
    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for("view_thread", thread_id=thread_id))


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