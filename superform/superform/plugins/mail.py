import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException
from flask import current_app
import json

FIELDS_UNAVAILABLE = ['Title', 'Description']

CONFIG_FIELDS = ["sender", "receiver"]


def run(publishing, channel_config):
    json_data = json.loads(channel_config)
    sender = json_data['sender']
    receivers = json_data['receiver']
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receivers
    msg['Subject'] = publishing.title

    body = publishing.description
    msg.attach(MIMEText(body, 'plain'))

    try:
        smtpObj = smtplib.SMTP(current_app.config["SMTP_HOST"],current_app.config["SMTP_PORT"])
        if current_app.config["SMTP_STARTTLS"]:
            smtpObj.starttls()
        text = msg.as_string()
        smtpObj.sendmail(sender, receivers, text)
        smtpObj.quit()
    except SMTPException as e:
        #TODO should add log here
        print(e)