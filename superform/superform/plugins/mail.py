import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException
from flask import current_app
import json

from superform import db
from superform.models import State

FIELDS_UNAVAILABLE = ["Image"]

CONFIG_FIELDS = ["sender", "receiver"]
AUTH_FIELDS = False
POST_FORM_VALIDATIONS = {}


def run(publishing,channel_config):
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
        # TODO should add log here
        print(e)
    publishing.state = State.VALIDATED_SHARED.value
    db.session.commit()


# Methods from other groups :
def authenticate(channel_name, publishing_id):
    return "AlreadyAuthenticated"


def post_pre_validation(post):
    return 1;


# returns the name of an extra form, None if not needed
def get_template_new():
    return None


# returns the name of an extra form (pre-fillable), None if not needed
def get_template_mod():
    return None


def saveExtraFields(channel, form):
    return None


def deletable():
    return True


def delete(pub):
    pass
