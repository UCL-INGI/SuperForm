import ast
import io
import re

from datetime import datetime
from flask import Blueprint, render_template, send_file
from rfeed import *
from superform.models import db, Channel, Post, Publishing, StatusCode
from superform.utils import login_required, get_instance_from_module_path

FIELDS_UNAVAILABLE = ['Publication Date']
CONFIG_FIELDS = ['channel_title', 'channel_description', 'channel_author']


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

# ======================= RSS page ====================

rss_page = Blueprint('rss', __name__)


@rss_page.route('/rss/<int:id>.xml', methods=["GET"])
@login_required()
def display_rss_feed(id):
    c = Channel.query.get(id)
    if c is None or c.module != "superform.plugins.rss":
        return render_template("404.html")
    clas = get_instance_from_module_path('superform.plugins.rss')
    config_fields = clas.CONFIG_FIELDS
    d = {}  # ['channel_title', 'channel_description', 'channel_author']
    if c.config is not "":
        d = ast.literal_eval(c.config)

    Pubdb = db.session.query(Publishing).filter(Publishing.channel_id == id)
    items = []
    for Publi in Pubdb:
        if Publi.state == 1 and Publi.date_from <= datetime.now() <= Publi.date_until:  # check if send
            author = db.session.query(Post).filter(Post.id == Publi.post_id).first()
            item1 = Item(
                title=Publi.title,
                link=Publi.image_url,
                description=Publi.description,
                author=author,  # channel_config['channel_author'],
                guid=Guid(Publi.link_url),
                pubDate=Publi.date_from)  # datetime(2017, 8, 1, 4, 0))
            items.append(item1)

    feed = Feed(
        title=d['channel_title'],  # channel name
        link='',  # channel_config['channel_location'],
        description=d['channel_description'],  # channel_config['channel_decription'],
        language="en-US",
        lastBuildDate=datetime.now(),
        items=items)

    generated_file = feed.rss()

    proxy = io.StringIO()
    proxy.write(generated_file)

    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))

    mem.seek(0)
    proxy.close()

    return send_file(
        mem,
        as_attachment=True,
        attachment_filename='feed.xml',
        mimetype='text/xml'
    )
