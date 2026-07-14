# Bulk Mailer

A Flask-based web application for sending personalized, automated bulk emails via SMTP. 

## Features

- **Web Interface**: Easy-to-use UI to configure SMTP credentials, email subject, and body.
- **CSV Upload**: Upload a list of contacts containing at least a `Name` and `Email` column.
- **Personalization**: Use `{name}` in your email body to dynamically personalize each message.
- **Background Processing**: Emails are sent in the background so the UI remains responsive.
- **Live Status Tracking**: Monitor the progress of your email campaign (total, sent, failed) in real-time.
- **Rate Limiting**: Built-in 1-second delay between emails to respect SMTP server limits.
- **HTML Support**: Send rich HTML emails; newlines in the web form are automatically converted to `<br>`.

## Prerequisites

- Python 3.x
- An SMTP server (e.g., Gmail, Outlook, Amazon SES)
  - *Note: If using Gmail, you will need to generate an [App Password](https://support.google.com/accounts/answer/185833).*

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/machphy/bulk_mailer.git
   cd bulk_mailer
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```
2. **Open your browser** and navigate to `http://127.0.0.1:5000`.
3. **Fill out the form**:
   - Provide your SMTP server details (e.g., `smtp.gmail.com` and port `587`).
   - Enter your email address and password (or App Password).
   - Write your Subject and Message Body (use `{name}` for personalization).
   - Upload your `contacts.csv` file.
4. **Send**: Click send and watch the live status updates!

## CSV Format

Your CSV file must include columns for the recipient's name and email address. The application is flexible and will look for any column containing the word "name" and "email" (case-insensitive).

Example `contacts.csv`:
```csv
Name,Email
John Doe,john.doe@example.com
Jane Smith,jane.smith@example.com
```

## Deployment

This application includes a `Procfile` and is ready to be deployed to platforms like [Render](https://render.com) or [Heroku](https://heroku.com/).
