from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
from pathlib import Path
import os

# mail_server = "smtp.gmail.com"
# port = 587
mail_ID = os.environ.get("Email_ID")
pwd = os.environ.get("Python_Pass")
receiver = os.environ.get("Receiver")

message = "Alert for investment"

try:
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Reminder for MF Investment"
    msg['From'] = "Reminder_MF"
    msg['To'] = "You"
    body_html = "<p> Alert for Investment </p>"
    msg_body = MIMEText(body_html, 'html')
    msg.attach(msg_body)
    mail_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    mail_server.login(mail_ID,pwd)
    mail_server.sendmail(mail_ID, receiver,msg.as_string())
except Exception as e:
    print(e)
finally:
    mail_server.close()
    print("End of execution!")