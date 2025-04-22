import os
import psycopg2
from flask import Flask, request, render_template_string
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

# PostgreSQL connection using environment variables
conn = psycopg2.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    dbname=os.environ.get('DB_NAME'),
    port=os.environ.get('DB_PORT', 5432)
)
cursor = conn.cursor()

@app.route('/')
def home():
    return "<h2>Welcome to the Farewell App!</h2><p>Visit /generate_qr to get the QR code.</p>"

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        usn = request.form['usn']
        name = request.form['name']
        phone = request.form['phone']

        # Validate against students table
        cursor.execute("SELECT * FROM students WHERE usn = %s", (usn,))
        student = cursor.fetchone()

        if student and student[1] == name and student[2] == phone:
            cursor.execute("INSERT INTO farewell (usn, name, phone) VALUES (%s, %s, %s)", (usn, name, phone))
            conn.commit()
            return render_template_string(f"<h2>Thank you {name}! Your attendance is recorded.</h2>")
        else:
            return render_template_string("<h2>Error: No matching record found.</h2>")

    form_html = """
    <h2>Mark Your Attendance</h2>
    <form method="POST">
        <label>USN:</label><br><input type="text" name="usn" required><br><br>
        <label>Name:</label><br><input type="text" name="name" required><br><br>
        <label>Phone:</label><br><input type="text" name="phone" required><br><br>
        <input type="submit" value="Submit">
    </form>
    """
    return render_template_string(form_html)

@app.route('/generate_qr')
def generate_qr():
    # Use your public Render URL here
    link = "https://farewell-0l2j.onrender.com/attendance" # Replace with your actual link

    # Generate QR code in memory
    img = qrcode.make(link)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Return HTML with embedded QR
    html = f"""
    <h2>Scan this QR Code to Mark Attendance</h2>
    <img src="data:image/png;base64,{img_base64}" alt="QR Code">
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
