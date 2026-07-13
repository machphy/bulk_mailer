from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import io
import time
import threading

app = Flask(__name__)

# Global state for tracking send progress
send_status = {
    "running": False,
    "total": 0,
    "sent": 0,
    "failed": 0,
    "log": []
}

def reset_status():
    send_status["running"] = False
    send_status["total"] = 0
    send_status["sent"] = 0
    send_status["failed"] = 0
    send_status["log"] = []

def send_emails_thread(recipients, subject, body_template, sender_email, sender_password, smtp_server, smtp_port):
    """Background thread to send emails one by one."""
    send_status["running"] = True
    send_status["total"] = len(recipients)
    send_status["sent"] = 0
    send_status["failed"] = 0
    send_status["log"] = []

    try:
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(sender_email, sender_password)
        send_status["log"].append("✅ Connected and logged in to SMTP server.")
    except Exception as e:
        send_status["log"].append(f"❌ SMTP Connection Failed: {e}")
        send_status["running"] = False
        return

    for recipient in recipients:
        # Create a lowercase dictionary for easier lookup of headers
        row_lower = {str(k).strip().lower(): v for k, v in recipient.items() if k is not None}
        
        email_addr = ""
        for key in row_lower:
            if 'email' in key:
                email_addr = row_lower[key].strip()
                break
                
        name = "Subscriber"
        for key in row_lower:
            if 'name' in key:
                name = row_lower[key].strip()
                break

        if not email_addr:
            send_status["failed"] += 1
            send_status["log"].append(f"⚠️ Skipped row with missing email.")
            continue

        try:
            personalized_body = body_template.replace("{name}", name)
        except Exception:
            personalized_body = body_template

        # Convert newlines to HTML breaks to preserve spacing from textarea
        personalized_body = personalized_body.replace('\n', '<br>')

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(personalized_body, "html"))

        try:
            server.send_message(msg)
            send_status["sent"] += 1
            send_status["log"].append(f"✅ Sent to {name} &lt;{email_addr}&gt;")
        except Exception as e:
            send_status["failed"] += 1
            send_status["log"].append(f"❌ Failed for {email_addr}: {e}")

        time.sleep(1)  # Rate limit

    try:
        server.quit()
    except:
        pass

    send_status["log"].append("🏁 All emails processed.")
    send_status["running"] = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/send", methods=["POST"])
def send():
    if send_status["running"]:
        return jsonify({"error": "A send operation is already in progress."}), 400

    reset_status()

    smtp_server = request.form.get("smtp_server", "smtp.gmail.com")
    smtp_port = request.form.get("smtp_port", "587")
    sender_email = request.form.get("sender_email", "")
    sender_password = request.form.get("sender_password", "")
    subject = request.form.get("subject", "")
    body = request.form.get("body", "")

    csv_file = request.files.get("csv_file")
    if not csv_file:
        return jsonify({"error": "No CSV file uploaded."}), 400

    # Parse CSV
    try:
        stream = io.StringIO(csv_file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)
        recipients = list(reader)
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {e}"}), 400

    if not recipients:
        return jsonify({"error": "CSV file is empty or has no valid rows."}), 400

    # Start background thread
    thread = threading.Thread(
        target=send_emails_thread,
        args=(recipients, subject, body, sender_email, sender_password, smtp_server, smtp_port),
        daemon=True
    )
    thread.start()

    return jsonify({"message": f"Started sending to {len(recipients)} recipients."})


@app.route("/status")
def status():
    return jsonify(send_status)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
