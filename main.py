from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib
import os
import imaplib
import email
import datetime
import time

start =time.time()
imap_server = "imap.gmail.com"
imap_port = 993
mail_ID = os.environ.get("Email")
pwd = os.environ.get("MF_AP")
receiver = os.environ.get("Receiver")
def send_mail(data):    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Reminder for MF Investment"
        msg['From'] = "Reminder_MF"
        msg['To'] = "You"
        body_html = "<p> Alert for Investment <br> Total amount to be invested = {data}</p>".format(data=data)
        msg_body = MIMEText(body_html, 'html')
        msg.attach(msg_body)
        mail_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        mail_server.login(mail_ID,pwd)
        mail_server.sendmail(mail_ID, os.environ.get("Receiver"),msg.as_string())
    except Exception as e:
        print(e)
    finally:
        mail_server.close()
        print("End of execution!")




def read_mail():
    #connecting to gmail server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(mail_ID,pwd)
    Subject = "Transaction alert for your ICICI Bank Credit Card"
    mail.select("inbox")
    yesterday = datetime.date.today() - datetime.timedelta(days = 1)
    day_bef = datetime.date.today() - datetime.timedelta(days = 2)
    criteria = day_bef.strftime("%d-%b-%Y")
    _, searched_data = mail.search(None,'UNSEEN') 
    
    amount = 0
    for searched in searched_data[0].split():
        data_to_return ={}
        _, mail_data = mail.fetch(searched,"(RFC822)")
        _, data = mail_data[0]
        message = email.message_from_bytes(data)
        
        if str(message["Date"][5:16]) == day_bef.strftime("%d %b %Y") and message["Subject"] == Subject:
            headers = ["From","To","Date","Subject"]
            for header in headers:
                data_to_return[header] = message[header]
            
            for msg in message.walk():
                if msg.get_content_type() == "text/html":
                    data_to_return["Body"] = msg.get_payload(decode=False)
                    
                    if "declined" not in data_to_return["Body"]:
                        a = data_to_return["Body"].split("INR")[1].split("on")[0].strip()
                        amount = amount+float(a)
                        
    send_mail(amount)                 
    mail.close()
    mail.logout()
    
read_mail()
end = time.time()
print(start-end)