from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import imaplib
import email
import datetime
import time
import logging
import mysql.connector

start =time.time()
imap_server = "imap.gmail.com"

# getting credentials from environment varibales
mail_ID = os.environ.get("Email")
pwd = os.environ.get("MF_AP")
receiver = os.environ.get("Receiver")

# initiating connection to database
mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("DB_pass"),
        database="my_expenses"
    )
cursor = mydb.cursor()



# Method to send the e-mail
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
        logging.error("Error in send_mail(data).")
    finally:
        mail_server.close()
        logging.info("End of execution")




# Method to read the mail
def read_mail():
    # connecting to gmail server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(mail_ID,pwd)
    Subject = "Transaction alert for your ICICI Bank Credit Card"
    mail.select("inbox")
    yesterday = datetime.date.today() - datetime.timedelta(days = 1)
    day_bef = datetime.date.today() - datetime.timedelta(days = 2)
    criteria = yesterday.strftime("%d-%b-%Y")
    _, searched_data = mail.search(None,'(FROM "credit_cards@icicibank.com" SUBJECT "Transaction alert for your ICICI Bank Credit Card" SINCE "{}")'.format(criteria)) 
    amount = 0
    
    for searched in searched_data[0].split():
        data_to_return ={}
        _, mail_data = mail.fetch(searched,"(RFC822)")
        _, data = mail_data[0]
        message = email.message_from_bytes(data)
        
        
        if str(message["Date"][5:16]) == yesterday.strftime("%d %b %Y") and message["Subject"] == Subject:
            # the below code is not needed till logging.info(data_to_return) but we can use it to keep track of amount spent on different dates.
            headers = ["From","To","Date","Subject"]
            for header in headers:
                data_to_return[header] = message[header]
            logging.info(data_to_return)

            
            for msg in message.walk():
                if msg.get_content_type() == "text/html":
                    data_to_return["Body"] = msg.get_payload(decode=False)
                    

                    if "declined" not in data_to_return["Body"]:
                        a = data_to_return["Body"].split("INR")[1].split("on")[0].strip()
                        try:
                            a = float(a)
                        except ValueError:
                            a = a.replace(',', '')
                            a = float(a)
                        amount = amount + a
                        spent_on = data_to_return["Body"].split("Info:")[1].split(".")[0]
                        logging.info(f"Amount = {a}")
                        logging.info(f"Money spent on = {spent_on}")
                        cursor.execute(f"INSERT INTO expense_spent (amount,spent_on) VALUES ('{a}','{spent_on}')")

                        date_from_mail = data_to_return["Date"]
                        date_object = datetime.datetime.strptime(date_from_mail, '%a, %d %b %Y %H:%M:%S %z')
                        formatted_date = date_object.strftime("%Y-%m-%d")
                        logging.info(f"Formatted date: {formatted_date}")

                        cursor.execute(f"INSERT INTO expenses (date,amount,spent_on) VALUES ('{formatted_date}','{amount}','{spent_on}')")
                    else:
                        logging.info(f"Declined mail(s) found.")


    date_today = datetime.date.today()
    cursor.execute(f"INSERT INTO expense_2 (date,Amount) VALUES ('{date_today}',{amount})")
    mydb.commit()
    logging.info(f"Amount ={amount}")
    send_mail(amount)                 
    mail.close()
    mail.logout()
logging.basicConfig(level=logging.INFO, filename="log.log",filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

read_mail()
end = time.time()
logging.info(f"Time taken ={start-end}")