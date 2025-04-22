from flask import Flask, request, render_template
import mysql.connector
import os

app = Flask(__name__)

db = mysql.connector.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    database=os.environ['DB_NAME']
)
cursor = db.cursor()

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        name = request.form['name']
        usn = request.form['usn']
        phone = request.form['phone']

        cursor.execute("SELECT * FROM students WHERE usn=%s AND name=%s AND phone=%s", (usn, name, phone))
        if cursor.fetchone():
            cursor.execute("SELECT * FROM farewell WHERE usn=%s", (usn,))
            if cursor.fetchone():
                message = "✅ Already marked as paid."
            else:
                cursor.execute("INSERT INTO farewell (usn, name, phone) VALUES (%s, %s, %s)", (usn, name, phone))
                db.commit()
                message = "✅ You have paid. Entry confirmed!"
        else:
            message = "❌ Details not found. Please contact coordinator."

    return render_template("form.html", message=message)

if __name__ == "__main__":
    app.run()
