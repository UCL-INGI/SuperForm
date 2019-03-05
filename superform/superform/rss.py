from flask import Blueprint, render_template, send_file
from superform.models import db, Publishing, Channel, Post
from rfeed import *
import io
import ast
from superform.utils import login_required, get_instance_from_module_path, get_modules_names, get_module_full_name
from datetime import datetime, timedelta

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
