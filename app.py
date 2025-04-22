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

        if student and student[1].strip().lower() == name.strip().lower() and student[2].strip() == phone.strip():
            # Add to farewell
            cursor.execute("INSERT INTO farewell (usn, name, phone) VALUES (%s, %s, %s)", (usn, name, phone))
            
            # Remove from students
            cursor.execute("DELETE FROM students WHERE usn = %s", (usn,))
            
            conn.commit()
            return render_template_string(f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Entry Ticket</title>
                        <style>
                            body {{
                                background-color: #f8fafc;
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                            }}
                            .ticket {{
                                background: #ffffff;
                                border: 2px dashed #4f46e5;
                                border-radius: 15px;
                                padding: 30px 40px;
                                width: 350px;
                                text-align: center;
                                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                            }}
                            .ticket h1 {{
                                color: #4f46e5;
                                margin-bottom: 10px;
                            }}
                            .ticket p {{
                                margin: 5px 0;
                                font-size: 18px;
                                color: #333;
                            }}
                            .thank-you {{
                                margin-top: 20px;
                                font-size: 16px;
                                color: #10b981;
                                font-weight: bold;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="ticket">
                            <h1>🎟️ Entry Ticket</h1>
                            <p><strong>Name:</strong> {name}</p>
                            <p><strong>USN:</strong> {usn}</p>
                            <p><strong>Phone:</strong> {phone}</p>
                            <div class="thank-you">✔️ Attendance Confirmed — Enjoy the Farewell!</div>
                        </div>
                    </body>
                    </html>
                    """)
        else:            
            return render_template_string(f"<h2>Error: No matching record found.</h2>")

    form_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Farewell Attendance</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #f3f4f6;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding-top: 50px;
                }
                .form-container {
                    background: white;
                    padding: 30px 40px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    max-width: 400px;
                    width: 90%;
                }
                h2 {
                    margin-bottom: 20px;
                    text-align: center;
                    color: #333;
                }
                label {
                    display: block;
                    margin-top: 15px;
                    font-weight: bold;
                    color: #444;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 10px;
                    margin-top: 5px;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    font-size: 16px;
                }
                input[type="submit"] {
                    width: 100%;
                    padding: 12px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    margin-top: 25px;
                    cursor: pointer;
                    transition: background 0.3s ease;
                }
                input[type="submit"]:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <div class="form-container">
                <h2>GET YOUR COUPON!</h2>
                <form method="POST">
                    <label for="usn">USN</label>
                    <input type="text" id="usn" name="usn" required>
        
                    <label for="name">Name (Enter Full Name as on ID Card)</label>
                    <input type="text" id="name" name="name" required>
        
                    <label for="phone">Phone Number (Do NOT enter +91) </label>
                    <input type="text" id="phone" name="phone" required>
        
                    <input type="submit" value="Submit">
                </form>
            </div>
        </body>
        </html>
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
