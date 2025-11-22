import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_smtp(sender_email, password, to_email, subject, body, attachments=None):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attachments
    if attachments:
        from email.mime.base import MIMEBase
        from email import encoders
        import os
        for path in attachments:
            part = MIMEBase('application', 'octet-stream')
            with open(path, 'rb') as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(path)}')
            msg.attach(part)

    # Connect to Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, msg.as_string())
