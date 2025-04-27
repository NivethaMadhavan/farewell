import os
import psycopg2
from flask import Flask, request, render_template_string

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

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        usn = request.form['usn'].strip().upper()

        # Check if USN exists in students table
        cursor.execute("SELECT usn FROM students WHERE usn = %s", (usn,))
        student = cursor.fetchone()

        if student:
            # Move USN to farewell table
            cursor.execute("INSERT INTO farewell (usn) VALUES (%s)", (usn,))
            cursor.execute("DELETE FROM students WHERE usn = %s", (usn,))
            conn.commit()
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Success</title>
                </head>
                <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 100px;">
                    <h2 style="color: green;">✅ Enjoy your food!</h2>
                </body>
                </html>
            """)
        else:
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Not Found</title>
                </head>
                <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 100px;">
                    <h2 style="color: red;">❌ Sorry, you are not eligible.</h2>
                </body>
                </html>
            """)

    # Form for entering USN
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Farewell Coupon Check</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #f3f4f6;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding-top: 100px;
                }
                .form-container {
                    background: white;
                    padding: 30px 40px;
                    border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                    max-width: 400px;
                    width: 90%;
                    text-align: center;
                }
                input[type="text"] {
                    width: 100%;
                    padding: 12px;
                    margin-top: 20px;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    font-size: 18px;
                    text-transform: uppercase;
                }
                input[type="submit"] {
                    width: 100%;
                    padding: 12px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 18px;
                    margin-top: 20px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #45a049;
                }
            </style>
        </head>
        <body>
            <div class="form-container">
                <h2>Enter Your USN</h2>
                <form method="POST">
                    <input type="text" name="usn" placeholder="Enter your USN" required>
                    <input type="submit" value="Check">
                </form>
            </div>
        </body>
        </html>
    """)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
