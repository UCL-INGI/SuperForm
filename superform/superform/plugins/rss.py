from datetime import datetime, timedelta
from flask import flash, Blueprint, redirect, url_for, request
import json
from xml.sax import saxutils
from superform.models import Publishing, db, Channel
from superform.suputils import selenium_utils, plugin_utils
from rfeed import *
import ast

FIELDS_UNAVAILABLE = ['Publication Date']
CONFIG_FIELDS = ['channel_title', 'channel_description', 'channel_author']

AUTH_FIELDS = False
POST_FORM_VALIDATIONS = {
    'title_max_length': 40000,
    'description_max_length': 40000,
    'image_type': 'url'
}

slack_error_callback_page = Blueprint('slack_error', 'channels')
slack_verify_callback_page = Blueprint('slack', 'channels')

def post_pre_validation(post):
    return plugin_utils.post_pre_validation_plugins(post, 40000, 40000)

def authenticate(channel_id, publishing_id):
    return 'AlreadyAuthenticated'

def run(publishing, channel_config):
    publishing.state = 1
    db.session.commit()

def saveExtraFields(channel, form):
    return None

# returns the name of an extra form, None if not needed
def get_template_new():
    return None

# returns the name of an extra form (pre-fillable), None if not needed
def get_template_mod():
    return None
def deletable():
    return True

def delete(pub):
    pass
