import json

from flask import Blueprint, url_for, current_app, request, redirect, session, render_template, flash

from superform.users import channels_available_for_user
from superform.utils import login_required, datetime_converter, str_converter, get_instance_from_module_path, \
    get_modules_names, get_module_full_name, datetime_now, str_converter_with_hour
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
    if form.get('datefrompost') is '':
        # set default date if no date was chosen
        date_from = date.today()
    else:
        date_from = datetime_converter(form.get('datefrompost'))
    if form.get('dateuntilpost') is '':
        date_until = date.today() + timedelta(days=7)
    else:
        date_until = datetime_converter(form.get('dateuntilpost'))
    p = Post(user_id=user_id, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()
    return p


def create_a_publishing(post, chn, form):  # called in publish_from_new_post()

    chan = str(chn.name)
    validate = pre_validate_post(chn, post)
    if validate == -1 or validate == 0:
        return validate

    title_post = form.get(chan + '_titlepost') if (form.get(chan + '_titlepost') is not None) else post.title
    descr_post = form.get(chan + '_descriptionpost') if form.get(
        chan + '_descriptionpost') is not None else post.description
    link_post = form.get(chan + '_linkurlpost') if form.get(chan + '_linkurlpost') is not None else post.link_url
    image_post = form.get(chan + '_imagepost') if form.get(chan + '_imagepost') is not None else post.image_url

    plugin = import_module(chn.module)
    if "saveExtraFields" in vars(plugin):
        misc_post = plugin.saveExtraFields(chan, form)  # plugin will handle extra fields here

    if form.get(chan + 'datefrompost') is '':
        date_from = date.today()
    else:
        date_from = datetime_converter(form.get(chan + '_datefrompost')) if datetime_converter(
            form.get(chan + '_datefrompost')) is not None else post.date_from
    if form.get(chan + 'dateuntilpost') is '':
        date_until = date.today() + timedelta(days=7)
    else:
        date_until = datetime_converter(form.get(chan + '_dateuntilpost')) if datetime_converter(
            form.get(chan + '_dateuntilpost')) is not None else post.date_until
    if chn.module == 'superform.plugins.ICTV':
        logo = form.get(chan + '_logo')
        subtitle = form.get(chan + '_subtitle')
        duration = form.get(chan + '_duration')

        pub = Publishing(post_id=post.id, channel_id=chn.id, state=0, title=title_post, description=descr_post,
                         link_url=link_post, image_url=image_post,
                         date_from=date_from, date_until=date_until, logo=logo, subtitle=subtitle, duration=duration)
        db.session.add(pub)
        db.session.commit()
    else:

        latest_version_publishing = db.session.query(Publishing).filter(Publishing.post_id == post.id,
                                                                        Publishing.channel_id == chn.id).order_by(
            Publishing.num_version.desc()).first()
        if latest_version_publishing is None:
            pub = Publishing(post_id=post.id, channel_id=chn.id, state=State.NOT_VALIDATED.value, title=title_post,
                             description=descr_post,
                             link_url=link_post, image_url=image_post,
                             date_from=date_from, date_until=date_until, misc=misc_post)

            db.session.add(pub)
            db.session.commit()

            user_comment = ""
            date_user_comment = str_converter_with_hour(datetime_now())
            comm = Comment(publishing_id=pub.publishing_id, user_comment=user_comment,
                           date_user_comment=date_user_comment)

            db.session.add(comm)
            db.session.commit()
        else:
            pub = Publishing(num_version=latest_version_publishing.num_version + 1, post_id=post.id, channel_id=chn.id,
                             state=State.NOT_VALIDATED.value, title=title_post, description=descr_post,
                             link_url=link_post, image_url=image_post,
                             date_from=date_from, date_until=date_until, misc=misc_post)

            db.session.add(pub)
            db.session.commit()
    return pub


@posts_page.route('/new', methods=['GET', 'POST'])
@login_required()
def new_post():
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    list_of_channels = channels_available_for_user(user_id)
    extraForms = {}
    for elem in list_of_channels:
        m = elem.module
        plugin = import_module(m)
        extraForms[elem.name] = plugin.get_template_new()
        clas = get_instance_from_module_path(m)
        unavailable_fields = ','.join(clas.FIELDS_UNAVAILABLE)
        setattr(elem, "unavailablefields", unavailable_fields)
        setattr(elem, "plugin_name", str(m))

    if request.method == "GET":  # when clicking on the new post tab
        # set default date
        default_date = {'from': date.today(), 'until': date.today() + timedelta(days=7)}

        post_form_validations = get_post_form_validations()

        return render_template('new.html', extra_forms=extraForms, l_chan=list_of_channels, post_form_validations=post_form_validations,
                               date=default_date)
    else:
        create_a_post(request.form)
        return redirect(url_for('index'))


@posts_page.route('/publish', methods=['POST'])
@login_required()
def publish_from_new_post():  # when clicking on 'save and publish' button
    # First create the post
    p = create_a_post(request.form)
    # then treat the publish part
    if request.method == "POST":
        error_id = "";
        state_error = False;
        for elem in request.form:
            if elem.startswith("chan_option_"):
                def substr(elem):
                    import re
                    return re.sub('^chan\_option\_', '', elem)

                c = Channel.query.get(substr(elem))
                validate = pre_validate_post(c, p)
                if validate == 0:
                    state_error = True
                    error_id = str(p.id) + ","
                # for each selected channel options
                # create the publication
                create_a_publishing(p, c, request.form)
        if state_error:
            error_id = error_id[:-1]
            error = "error in post :", error_id, " field(s) not valid"
            flash(error, "danger")
            return redirect(url_for('index'))
    db.session.commit()
    return redirect(url_for('index'))


@posts_page.route('/records')
@login_required()
def records():
    posts = db.session.query(Post).filter(Post.user_id == session.get("user_id", ""))
    records = [(p) for p in posts if p.is_a_record()]
    return render_template('records.html', records=records)


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
        date_user_comment = str_converter_with_hour(datetime_now())
        comm = Comment(publishing_id=new_pub.publishing_id, user_comment=user_comment,
                       date_user_comment=date_user_comment)
        db.session.add(comm)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        pub_versions = db.session.query(Publishing).filter(Publishing.post_id == pub.post_id, Publishing.channel_id == pub.channel_id). \
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

        return render_template('resubmit_post.html', pub=pub, channel=chn, pub_versions=pub_versions, pub_comments=pub_comments_json, comments=pub_comments, post_form_validations=post_form_validations)


def create_a_resubmit_publishing(pub, chn, form):

    validate = pre_validate_post(chn, pub)
    if validate == -1 or validate == 0:
        return validate

    title_post = form.get('titlepost')
    descr_post = form.get('descrpost')
    link_post = form.get('linkurlpost')
    image_post = form.get('imagepost')
    if chn.module == 'superform.plugins.gcal':
        pub.date_start = datetime_converter(form.get('datedebut'))
        pub.hour_start = form.get('heuredebut')
        pub.date_end = datetime_converter(form.get('datefin'))
        pub.hour_end = form.get('heurefin')
        pub.location = form.get('location')
        pub.color = form.get('color')
        pub.visibility = form.get('visibility')
        pub.availability = form.get('availability')
    else:
        date_from = datetime_converter(form.get('datefrompost'))
        date_until = datetime_converter(form.get('dateuntilpost'))

    latest_version_publishing = db.session.query(Publishing).filter(Publishing.post_id == pub.post_id,
                                                                    Publishing.channel_id == chn.id).order_by(
                                                                    Publishing.num_version.desc()
                                                                    ).first()
    new_pub = Publishing(num_version=latest_version_publishing.num_version + 1, post_id=pub.post_id, channel_id=chn.id,
                     state=State.NOT_VALIDATED.value, title=title_post, description=descr_post,
                     link_url=link_post, image_url=image_post,
                     date_from=date_from, date_until=date_until)
    return new_pub


def pre_validate_post(channel, post):
    plugin = import_module(channel.module)
    return plugin.post_pre_validation(post)


def get_post_form_validations():
    mods = get_modules_names(current_app.config["PLUGINS"].keys())
    post_form_validations = dict()
    for m in mods:
        full_name = get_module_full_name(m)
        clas = get_instance_from_module_path(full_name)
        fields = clas.POST_FORM_VALIDATIONS
        post_form_validations[m] = fields
    return post_form_validations

