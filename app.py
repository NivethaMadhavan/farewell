import os
import psycopg2
from flask import Flask, request, render_template_string
import qrcode

app = Flask(__name__)

# PostgreSQL connection using environment variables (local setup)
conn = psycopg2.connect(
    host=os.environ.get('DB_HOST'),        # Use environment variable for host
    user=os.environ.get('DB_USER'),        # Use environment variable for user
    password=os.environ.get('DB_PASSWORD'), # Use environment variable for password
    dbname=os.environ.get('DB_NAME'),       # Use environment variable for db name
    port=os.environ.get('DB_PORT', 5432)    # Default PostgreSQL port is 5432
)

cursor = conn.cursor()

@app.route('/')
def index():
    return "Hello, Welcome to the Farewell App!"

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        # Get user input
        usn = request.form['usn']
        name = request.form['name']
        phone = request.form['phone']
        
        # Check if the student exists in the database
        cursor.execute("SELECT * FROM students WHERE usn = %s", (usn,))
        student = cursor.fetchone()

        if student and student[1] == name and student[2] == phone:
            # Add student to farewell table
            cursor.execute("INSERT INTO farewell (usn, name, phone) VALUES (%s, %s, %s)", (usn, name, phone))
            conn.commit()
            success_html = f"<h1>Thank you, {name}! You have successfully marked your attendance.</h1>"
            return render_template_string(success_html)
        else:
            error_html = "<h1>Error: No matching record found!</h1>"
            return render_template_string(error_html)

    # If GET request, show attendance form
    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Attendance Form</title>
    </head>
    <body>
        <h1>Fill in your details to mark attendance</h1>
        <form method="POST">
            <label for="usn">USN:</label>
            <input type="text" id="usn" name="usn" required><br><br>

            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required><br><br>

            <label for="phone">Phone Number:</label>
            <input type="text" id="phone" name="phone" required><br><br>

            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)

@app.route('/generate_qr')
def generate_qr():
    # URL of the attendance page
    link = "http://localhost:5000/attendance"
    
    # Generate QR code
    img = qrcode.make(link)
    img.save("static/farewell_qr.png")
    
    return "QR Code generated successfully!"

if __name__ == '__main__':
    app.run(debug=True)
