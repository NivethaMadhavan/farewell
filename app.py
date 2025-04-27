import os
import psycopg2
from flask import Flask, request, render_template_string

app = Flask(__name__)

# PostgreSQL connection
conn = psycopg2.connect(
    host=os.environ.get('DB_HOST'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    dbname=os.environ.get('DB_NAME'),
    port=os.environ.get('DB_PORT', 5432)
)
cursor = conn.cursor()

@app.route('/', methods=['GET', 'POST'])
def check_coupon():
    message = ""
    if request.method == 'POST':
        usn = request.form['usn'].strip().upper()

        # Check if USN exists in 'coupon' table
        cursor.execute("SELECT * FROM coupon WHERE usn = %s", (usn,))
        record = cursor.fetchone()

        if record:
            # Move to 'coupon_used'
            cursor.execute("INSERT INTO coupon_used (usn) VALUES (%s)", (usn,))
            cursor.execute("DELETE FROM coupon WHERE usn = %s", (usn,))
            conn.commit()
            message = "<h2 style='color:green;'>✅ You can eat! Enjoy!</h2>"
        else:
            message = "<h2 style='color:red;'>❌ Sorry, no coupon found.</h2>"

    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coupon Check</title>
        <style>
            body {{
                background-color: #f8fafc;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                flex-direction: column;
            }}
            form {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                text-align: center;
            }}
            input[type="text"] {{
                width: 100%;
                padding: 10px;
                margin-bottom: 20px;
                border-radius: 5px;
                border: 1px solid #ccc;
                font-size: 16px;
            }}
            input[type="submit"] {{
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
            }}
            input[type="submit"]:hover {{
                background-color: #45a049;
            }}
        </style>
    </head>
    <body>
        <form method="POST">
            <h2>Enter Your USN to Check Coupon</h2>
            <input type="text" name="usn" placeholder="Enter USN" required>
            <input type="submit" value="Check">
        </form>
        {message}
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
