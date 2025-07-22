from flask import Flask, render_template, request
import smtplib
from email.message import EmailMessage
import sqlite3
import random

app = Flask(__name__)

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "youremail@example.com"
    msg['To'] = "receiver@example.com"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("youremail@example.com", "yourpassword")
            smtp.send_message(msg)
    except Exception as e:
        print("Error sending email:", e)

def init_db():
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, temperature REAL, status TEXT)")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM alerts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("index.html", alerts=rows)

@app.route('/check')
def check_temperature():
    temp = random.uniform(20.0, 100.0)
    status = "NORMAL"
    if temp > 50:
        status = "ALERT"
        send_email("Temperature Alert", f"The current temperature is {temp:.2f}°C which exceeds the safe limit.")

    conn = sqlite3.connect('alerts.db')
    c = conn.cursor()
    c.execute("INSERT INTO alerts (temperature, status) VALUES (?, ?)", (temp, status))
    conn.commit()
    conn.close()

    return f"Temperature checked: {temp:.2f}°C - Status: {status}"

# ✅ Health check route for Render
@app.route('/healthz')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

