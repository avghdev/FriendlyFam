from flask import Flask, render_template, request, redirect, session
import mysql.connector
import gunicorn

app = Flask(__name__)
app.secret_key = "secret"



db = mysql.connector.connect(
    host = "us-cdbr-east-03.cleardb.com",
    user = "bc99de75d20aa7",
    password = "9eb5e0df",
    database = "heroku_4f28d9fbf145463"
)

mycursor = db.cursor()

# Create event table if it doesn't already exist
mycursor.execute("CREATE TABLE IF NOT EXISTS events (id INT AUTO_INCREMENT PRIMARY KEY," +
                 "host VARCHAR(255)," +
                 "description VARCHAR(255)," +
                 "day VARCHAR(255)," +
                 "time VARCHAR(255)," +
                 "status VARCHAR(255))")

# Create user table if it doesn't already exist
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY," +
                 "username VARCHAR(255)," +
                 "UNIQUE (username)," +
                 "password VARCHAR(255))")

@app.route('/')
def home():
    if "username" in session:
        sql = "SELECT id, host, description, day, time, status FROM events"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        
        # check if there is any results returned by query
        if len(myresult) == 0:
            list = ""
        else:
            list = myresult

        return render_template("home.html", user = session["username"], list=list)
    else:
        return render_template("index.html")

@app.route("/cancel/<int:id>")
def delete(id):
    status = "Canceled"

    sql = "UPDATE events SET status = %s WHERE id = %s"
    values = (status, id)
    mycursor.execute(sql, values)
    db.commit()

    return redirect("/")

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    if request.method == "POST":
        host = session["username"]
        description = request.form.get("description")
        day = request.form.get("day")
        time = request.form.get("time")
        status = request.form.get("status")

        sql = "UPDATE events SET host = %s, description = %s, day = %s, time = %s, status = %s WHERE id = %s"
        values = (host, description, day, time, status, id)
        mycursor.execute(sql, values)
        db.commit()

        return redirect("/")
    else:
        sql = "SELECT id, host, description, day, time, status FROM events WHERE id = %s"
        value = (id,)
        mycursor.execute(sql, value)
        result = mycursor.fetchone()

        return render_template("edit.html", event=result)

@app.route("/myevents")
def myevents():
    host = session["username"]
    sql = "SELECT id, host, description, day, time, status FROM events WHERE host = %s"
    value = (host,)
    mycursor.execute(sql, value)

    myresult = mycursor.fetchall()

    if len(myresult) == 0:
            list = ""
    else:
        list = myresult

    return render_template("myevents.html", user = session["username"], list=list)

@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        host = session["username"]
        description = request.form.get("description")
        day = request.form.get("day")
        time = request.form.get("time")
        status = "still on"

        sql = "INSERT INTO events(host, description, day, time, status) VALUES (%s, %s, %s, %s, %s)"
        values = [host, description, day, time, status]
        mycursor.execute(sql, values)

        db.commit()

        return redirect("/myevents")
    else:
        return render_template("add.html", user = session["username"])

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        sql = "SELECT username FROM users WHERE username = %s AND password = %s";
        values = [username, password]
        mycursor.execute(sql, values)

        myresult = mycursor.fetchall()

        if len(myresult) > 0:
            session["username"] = username
            return redirect("/")
        else:
            return render_template("index.html", message = "Incorrect username or password!")
    else:
        return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if (password != confirm_password):
            return render_template("signup.html", message="Passwords don't match!")

        # check if username already exists
        sql = "SELECT username FROM users WHERE username = %s";
        value = (username,)
        mycursor.execute(sql, value)

        myresult = mycursor.fetchall()

        if len(myresult) > 0:
            return render_template("signup.html", message = "Username already taken!")
        else:
            sql = "INSERT INTO users(username, password) VALUES (%s, %s)"
            values = (username, password)
            mycursor.execute(sql, values)
            db.commit()

            session["username"] = username
            return redirect("/")
    else:
        return render_template("signup.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template("index.html")


if __name__ == '__main__':
    app.run(HOST, PORT)
