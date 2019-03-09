import json

from flask import Blueprint, url_for, current_app, request, redirect, session, render_template, flash

from superform.publishings import create_a_publishing, get_post_form_validations
from superform.users import channels_available_for_user
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path, \
    get_modules_names, get_module_full_name, datetime_now
from superform.models import db, Post, Publishing, Channel, Comment, State, AlchemyEncoder

from importlib import import_module
from datetime import date, timedelta

posts_page = Blueprint('posts', __name__)


def create_a_post(form):  # called in publish_from_new_post() & new_post()
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    title_post = form.get('titlepost')
    descr_post = form.get('descriptionpost')
    link_post = form.get('linkurlpost')
    image_post = form.get('imagepost')

    # set default date if no date was chosen
    if form.get('datefrompost') is '':
        date_from = str_converter(date.today())
    else:
        date_from = datetime_converter(form.get('datefrompost'))
    if form.get('dateuntilpost') is '':
        date_until = str_converter(date.today() + timedelta(days=7))
    else:
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

    if request.method == "GET":  # when clicking on the new post tab
        ictv_data = None
        if len(ictv_chans) != 0:
            from plugins.ictv import process_ictv_channels
            ictv_data = process_ictv_channels(ictv_chans)

        # set default date
        default_date = {'from': date.today(), 'until': date.today() + timedelta(days=7)}
        post_form_validations = get_post_form_validations()

        return render_template('new.html', l_chan=list_of_channels, ictv_data=ictv_data,
                               post_form_validations=post_form_validations,
                               date=default_date)
    else:
        # Save as draft
        # FIXME Maybe refactor the code so that this part is not too confusing?
        create_a_post(request.form)
        flash("The post was successfully saved as draft", category='success')
        return redirect(url_for('index'))


@posts_page.route('/publish', methods=['POST'])
@login_required()
def publish_from_new_post():  # when clicking on 'save and publish' button
    # First create the post
    p = create_a_post(request.form)
    # then treat the publish part
    if request.method == "POST":
        for elem in request.form:
            if elem.startswith("chan_option_"):
                def substr(elem):
                    import re
                    return re.sub(r'^chan\_option\_', '', elem)

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


def create_a_resubmit_publishing(pub, chn, form):
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    title_post = form.get('titlepost')
    descr_post = form.get('descrpost')
    link_post = form.get('linkurlpost')
    image_post = form.get('imagepost')
    date_from = datetime_converter(form.get('datefrompost'))
    date_until = datetime_converter(form.get('dateuntilpost'))

    latest_version_publishing = db.session.query(Publishing).filter(Publishing.post_id == pub.post_id,
                                                                    Publishing.channel_id == chn.id).order_by(
        Publishing.num_version.desc()
    ).first()
    new_pub = Publishing(num_version=latest_version_publishing.num_version + 1, post_id=pub.post_id, channel_id=chn.id,
                         state=State.NOT_VALIDATED.value, user_id=user_id, title=title_post, description=descr_post,
                         link_url=link_post, image_url=image_post,
                         date_from=date_from, date_until=date_until)
    return new_pub


@posts_page.route('/publishing/resubmit/<int:id>', methods=["GET", "POST"])
@login_required()
def resubmit_publishing(id):
    pub = db.session.query(Publishing).filter(Publishing.publishing_id == id).first()
    chn = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
    if request.method == "POST":
        new_pub = create_a_resubmit_publishing(pub, chn, request.form)
        db.session.add(new_pub)
        pub.state = State.OLD_VERSION.value
        db.session.commit()

        user_comment = ""
        if request.form.get('user_comment'):
            user_comment = request.form.get('user_comment')
        date_user_comment = str_converter(datetime_now())
        comm = Comment(publishing_id=new_pub.publishing_id, user_comment=user_comment,
                       date_user_comment=date_user_comment)
        db.session.add(comm)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        pub_versions = db.session.query(Publishing).filter(Publishing.post_id == pub.post_id,
                                                           Publishing.channel_id == pub.channel_id). \
            order_by(Publishing.num_version.desc()).all()
        pub_ids = []
        for pub_ver in pub_versions:
            pub_ids.insert(0, pub_ver.publishing_id)
        pub_comments = db.session.query(Comment).filter(Comment.publishing_id.in_(pub_ids)).all()
        pub_versions = json.dumps(pub_versions, cls=AlchemyEncoder)
        pub_comments_json = json.dumps(pub_comments, cls=AlchemyEncoder)
        pub.date_from = str_converter(pub.date_from)
        pub.date_until = str_converter(pub.date_until)

        post_form_validations = get_post_form_validations()

        return render_template('resubmit_post.html', pub=pub, channel=chn, pub_versions=pub_versions,
                               pub_comments=pub_comments_json, comments=pub_comments,
                               post_form_validations=post_form_validations)
