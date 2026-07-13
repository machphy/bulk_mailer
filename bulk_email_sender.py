import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import time
import getpass
import os

def send_bulk_emails(csv_file, subject, body_template, sender_email, sender_password, smtp_server, smtp_port):
    """
    Sends separate emails to a list of recipients from a CSV file.
    
    The CSV file should have columns like 'name' and 'email'.
    """
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Please create it first.")
        return

    print(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
    try:
        # Set up the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Secure the connection
        server.login(sender_email, sender_password)
        print("Login successful.\n")

        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipient_email = row['email']
                recipient_name = row.get('name', 'Subscriber')
                
                # Personalize the email body if you have {name} in the template
                personalized_body = body_template.format(name=recipient_name)

                # Create the email message
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(personalized_body, 'plain')) # change to 'html' if sending HTML emails

                try:
                    server.send_message(msg)
                    print(f"Successfully sent email to {recipient_name} <{recipient_email}>")
                except Exception as e:
                    print(f"Failed to send email to {recipient_email}: {e}")
                
                # Small delay to avoid rate limits and getting flagged as spam
                time.sleep(1)

        server.quit()
        print("\nFinished sending bulk emails!")

    except Exception as e:
        print(f"Error connecting to server or logging in: {e}")

if __name__ == "__main__":
    print("--- Bulk Email Sender ---")
    
    # --- Configuration ---
    # Update these details with your email provider's settings.
    # For Gmail, you will likely need to generate an App Password if 2FA is enabled.
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    SENDER_EMAIL = input("Enter your email address: ")
    SENDER_PASSWORD = getpass.getpass("Enter your email password (or App Password): ")
    
    # Path to your CSV file
    CSV_FILE = "contacts.csv" 
    
    # Email Subject and Body
    SUBJECT = "Your Personalized Subject Here"
    BODY_TEMPLATE = "Hello {name},\n\nThis is a personalized email sent just for you.\n\nBest regards,\nRajeev"

    # Run the sender
    print(f"\nReady to send. Ensure you have configured '{CSV_FILE}' in the same directory.")
    confirm = input("Type 'yes' to start sending: ")
    
    if confirm.lower() == 'yes':
        send_bulk_emails(CSV_FILE, SUBJECT, BODY_TEMPLATE, SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT)
    else:
        print("Aborted.")
