import datetime
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from superform.users import channels_available_for_user

from superform.models import db, Channel, Post, Publishing, State, User
from superform.publishings import create_a_publishing
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path


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

    ictv_chans = []

    for elem in list_of_channels:
        m = elem.module

        clas = get_instance_from_module_path(m)
        unavailable_fields = ','.join(clas.FIELDS_UNAVAILABLE)
        setattr(elem, "unavailablefields", unavailable_fields)

        if 'ictv_data_form' in unavailable_fields:
            ictv_chans.append(elem)

    if request.method == "GET":
        ictv_data = None
        if len(ictv_chans) != 0:
            from plugins.ictv import process_ictv_channels
            ictv_data = process_ictv_channels(ictv_chans)

        return render_template('new.html', l_chan=list_of_channels, ictv_data=ictv_data)
    else:
        # Save as draft
        # FIXME Maybe refactor the code so that this part is not too confusing?
        create_a_post(request.form)
        flash("The post was successfully saved as draft", category='success')
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
    flash("The post was successfully submitted.", category='success')
    return redirect(url_for('index'))


@posts_page.route('/records')
@login_required()
def records():
    posts = db.session.query(Post).filter(Post.user_id == session.get("user_id", ""))
    records = [(p) for p in posts if p.is_a_record()]
    return render_template('records.html', records=records)
