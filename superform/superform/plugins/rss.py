from flask import flash, Blueprint, redirect, url_for, request
import re
from superform.models import Publishing, db, Channel, StatusCode

FIELDS_UNAVAILABLE = ['Publication Date']
CONFIG_FIELDS = ['channel_title', 'channel_description', 'channel_author']

slack_error_callback_page = Blueprint('slack_error', 'channels')
slack_verify_callback_page = Blueprint('slack', 'channels')


def post_pre_validation_plugins(post, maxLengthTitle, maxLengthDescription):
    pattern = '^(?:(?:https?|http?|wwww?):\/\/)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/\S*)?$';
    if len(post.title) > maxLengthTitle or len(post.title) == 0: return 0
    if len(post.description) > maxLengthDescription or len(post.description) == 0: return 0
    if post.link_url is not None and post.link_url and len(post.link_url) > 0:
        if re.match(pattern, post.link_url, 0) is None: return 0
    if post.image_url is not None and len(post.image_url) > 0:
        if re.match(pattern, post.image_url, 0) is None: return 0
    return 1


def post_pre_validation(post):
    return post_pre_validation_plugins(post, 40000, 40000)


def authenticate(channel_id, publishing_id):
    return 'AlreadyAuthenticated'


def run(publishing, channel_config):
    publishing.state = 1
    db.session.commit()
    return StatusCode.OK, None


def saveExtraFields(channel, form):
    return None


# returns the name of an extra form (pre-fillable), None if not needed
def get_template_mod():
    return None


def deletable():
    return True


def delete(pub):
    pass
