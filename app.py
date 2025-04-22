import os
import psycopg2
from flask import Flask, request, render_template
import qrcode

app = Flask(__name__)

# PostgreSQL connection using environment variables
conn = psycopg2.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    dbname=os.environ['DB_NAME'],
    port=os.environ.get('DB_PORT', 5432)  # Default to 5432 if no port is set
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
            return render_template('success.html', name=name)
        else:
            return "Error: No matching record found!"

    return render_template('attendance_form.html')

@app.route('/generate_qr')
def generate_qr():
    # URL of the attendance page
    link = "https://your-app-name.onrender.com/attendance"
    
    # Generate QR code
    img = qrcode.make(link)
    img.save("static/farewell_qr.png")
    
    return "QR Code generated successfully!"

if __name__ == '__main__':
    app.run(debug=True)
