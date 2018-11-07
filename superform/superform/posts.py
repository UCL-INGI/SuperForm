from flask import Blueprint, url_for, request, redirect, session, render_template

from superform.users import channels_available_for_user
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path
from superform.models import db, Post, Publishing, Channel
from superform.publishings import create_a_publishing

posts_page = Blueprint('posts', __name__)


def create_a_post(form):
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    title_post = form.get('titlepost')
    descr_post = form.get('descriptionpost')
    link_post = form.get('linkurlpost')
    image_post = form.get('imagepost')
    date_from = datetime_converter(form.get('datefrompost'))
    date_until = datetime_converter(form.get('dateuntilpost'))
    p = Post(user_id=user_id, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()
    return p


@posts_page.route('/new', methods=['GET', 'POST'])
@login_required()
def new_post():
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    list_of_channels = channels_available_for_user(user_id)
    for elem in list_of_channels:
        m = elem.module
        clas = get_instance_from_module_path(m)
        unaivalable_fields = ','.join(clas.FIELDS_UNAVAILABLE)
        setattr(elem, "unavailablefields", unaivalable_fields)

    if request.method == "GET":
        return render_template('new.html', l_chan=list_of_channels)
    else:
        create_a_post(request.form)
        return redirect(url_for('index'))


@posts_page.route('/publish', methods=['POST'])
@login_required()
def publish_from_new_post():
    # First create the post
    p = create_a_post(request.form)
    # then treat the publish part
    if request.method == "POST":
        for elem in request.form:
            if elem.startswith("chan_option_"):
                def substr(elem):
                    import re
                    return re.sub('^chan\_option\_', '', elem)

                c = Channel.query.get(substr(elem))
                # for each selected channel options
                # create the publication
                pub = create_a_publishing(p, c, request.form)

    db.session.commit()
    return redirect(url_for('index'))


@posts_page.route('/list_posts', methods=['GET'])
@login_required()
def get_all_posts():
    from sqlalchemy import desc
    posts = db.session.query(Post).filter(Post.user_id == session.get("user_id", "")).order_by(desc(Post.id))
    return render_template('list_posts.html', posts=posts)


@posts_page.route('/records')
@login_required()
def records():
    posts = db.session.query(Post).filter(Post.user_id == session.get("user_id", ""))
    records = [(p) for p in posts if p.is_a_record()]
    return render_template('records.html', records=records)
