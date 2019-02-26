import json

from datetime import date, timedelta
from flask import Blueprint, current_app, flash, url_for, request, redirect, session, render_template
from importlib import import_module

from plugins import gcal_plugin
from superform.channels import valid_conf
from superform.models import db, User, Publishing, Channel, Comment, State, AlchemyEncoder
from superform.users import get_moderate_channels_for_user
from superform.utils import login_required, datetime_converter, str_converter, datetime_now, get_modules_names, \
    get_module_full_name, get_instance_from_module_path

pub_page = Blueprint('publishings', __name__)


def create_a_publishing(post, chn, form):  # called in publish_from_new_post()
    chan = str(chn.name)
    plug = import_module(chn.module)
    title_post = form.get(chan + '_titlepost') if (form.get(chan + '_titlepost') is not None) else post.title
    # Team2 stat
    chn.count += 1
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    # Team2 stat

    if "twitter" in chn.module:
        descr_post = form.get('tweets')
    elif form.get(chan + '_descriptionpost') is not None:
        descr_post = form.get(chan + '_descriptionpost')
    else:
        descr_post = post.description

    # TEAM 3 ictv
    if 'forge_link_url' in dir(plug):
        link_post = plug.forge_link_url(chan, form)
    else:
        link_post = form.get(chan + '_linkurlpost') if form.get(
            chan + '_linkurlpost') is not None else post.link_url
    # TEAM 3 ictv

    image_post = form.get(chan + '_imagepost') if form.get(chan + '_imagepost') is not None else post.image_url

    if form.get(chan + 'datefrompost') is '':
        date_from = str_converter(date.today())
    else:
        date_from = datetime_converter(form.get(chan + '_datefrompost')) if datetime_converter(
            form.get(chan + '_datefrompost')) is not None else post.date_from
    if form.get(chan + 'dateuntilpost') is '':
        date_until = str_converter(date.today() + timedelta(days=7))
    else:
        date_until = datetime_converter(form.get(chan + '_dateuntilpost')) if datetime_converter(
            form.get(chan + '_dateuntilpost')) is not None else post.date_until

    latest_version_publishing = db.session.query(Publishing).filter(Publishing.post_id == post.id,
                                                                    Publishing.channel_id == chn.id).order_by(
        Publishing.num_version.desc()).first()

    if latest_version_publishing is None:
        pub = Publishing(post_id=post.id, user_id=user_id, channel_id=chn.id, state=State.NOT_VALIDATED.value,
                         title=title_post, description=descr_post,
                         link_url=link_post, image_url=image_post,
                         date_from=date_from, date_until=date_until)

        c = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
        if c is not None:
            plugin_name = c.module
            # If it is a pdf chanel we don't need to save it, printing it would be enough
            # TEAM6: MODIFICATION FOR PDF
            if str(plugin_name).endswith("pdf"):
                c_conf = c.config
                plugin = import_module(plugin_name)
                plugin.run(pub, c_conf)
                # Does not save the pdf posts
                return pub
            # END OF MODIFICATION

        if is_gcal_channel(chan) and not gcal_plugin.is_valid(pub):
            return None
        if is_gcal_channel(chan):
            generate_google_user_credentials(chan)

        db.session.add(pub)
        db.session.commit()

        user_comment = ""
        date_user_comment = str_converter(datetime_now())
        comm = Comment(publishing_id=pub.publishing_id, user_comment=user_comment,
                       date_user_comment=date_user_comment)

        db.session.add(comm)
        db.session.commit()
    else:
        pub = Publishing(num_version=latest_version_publishing.num_version + 1, post_id=post.id, user_id=user_id,
                         channel_id=chn.id, state=State.NOT_VALIDATED.value, title=title_post, description=descr_post,
                         link_url=link_post, image_url=image_post,
                         date_from=date_from, date_until=date_until)

        c = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
        if c is not None:
            plugin_name = c.module
            # If it is a pdf chanel we don't need to save it, printing it would be enough
            # TEAM6: MODIFICATION FOR PDF
            if str(plugin_name).endswith("pdf"):
                c_conf = c.config
                plugin = import_module(plugin_name)
                plugin.run(pub, c_conf)
                # Does not save the pdf posts
                return pub
            # END OF MODIFICATION

        if is_gcal_channel(chan) and not gcal_plugin.is_valid(pub):
            return None
        if is_gcal_channel(chan):
            generate_google_user_credentials(chan)

        db.session.add(pub)
        db.session.commit()

    return pub


# TEAM2 gcal
def is_gcal_channel(channel_id):
    c = db.session.query(Channel).filter(Channel.name == channel_id).first()
    return c.module.endswith('gcal_plugin')


def generate_google_user_credentials(channel_id):
    c = db.session.query(Channel).filter(Channel.name == channel_id).first()
    gcal_plugin.generate_user_credentials(c.config)


# TEAM2 gcal


@pub_page.route('/moderate/<int:id>/<string:idc>', methods=["GET", "POST"])
@login_required()
def moderate_publishing(id, idc):
    chn = db.session.query(Channel).filter(Channel.id == idc).first()
    """ FROM THIS : 
    SHOULD BE IN THE if request.method == 'GET' (BUT pub.date_from = str_converter(pub.date_from) PREVENT US)"""
    pub_versions = db.session.query(Publishing).filter(Publishing.post_id == id, Publishing.channel_id == idc). \
        order_by(Publishing.num_version.desc()).all()
    pub_ids = []
    for pub_ver in pub_versions:
        pub_ids.insert(0, pub_ver.publishing_id)
    pub_comments = db.session.query(Comment).filter(Comment.publishing_id.in_(pub_ids)).all()
    """TO THIS"""
    pub_versions = json.dumps(pub_versions, cls=AlchemyEncoder)
    pub_comments_json = json.dumps(pub_comments, cls=AlchemyEncoder)
    pub = db.session.query(Publishing).filter(Publishing.post_id == id, Publishing.channel_id == idc).order_by(
        Publishing.num_version.desc()).first()
    pub.date_from = str_converter(pub.date_from)
    pub.date_until = str_converter(pub.date_until)

    plugin_name = chn.module
    c_conf = chn.config
    plugin = import_module(plugin_name)
    notconfig = not valid_conf(c_conf, plugin.CONFIG_FIELDS)

    if request.method == "GET" or notconfig:
        """SHOULD PREPARE THE pub_versions AND pub_comments"""
        post_form_validations = get_post_form_validations()

        return render_template('moderate_post.html', pub=pub, channel=chn, pub_versions=pub_versions,
                               pub_comments=pub_comments_json, comments=pub_comments,
                               post_form_validations=post_form_validations, notconf=notconfig)
    else:
        pub.title = request.form.get('titlepost')
        pub.description = request.form.get('descrpost')
        pub.link_url = request.form.get('linkurlpost')
        pub.image_url = request.form.get('imagepost')
        pub.date_from = datetime_converter(request.form.get('datefrompost'))
        pub.date_until = datetime_converter(request.form.get('dateuntilpost'))

        if pub.state == 66:  # EDITION
            try:
                can_edit = plugin.can_edit(pub, c_conf)
                if can_edit:
                    plugin.edit(pub, c_conf)
                    pub.state = 1
                    db.session.commit()
                else:
                    pub.state = 1
                    db.session.commit()
            except AttributeError:
                pub.state = 1
                flash("Error : module don't implement can_edit or edit method")
                db.session.commit()
        else:
            # state is shared & validated
            pub.state = 1
            db.session.commit()
            # running the plugin here
            plugin.run(pub, c_conf)

        return redirect(url_for('index'))


@pub_page.route('/moderate', methods=["GET"])
@login_required()
def moderate():
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None
    flattened_list_pubs = []
    if user is not None:
        chans = get_moderate_channels_for_user(user)
        pubs_per_chan = (db.session.query(Publishing).filter((Publishing.channel_id == c.id) &
                                                             (Publishing.state == 0)) for c in chans)
        flattened_list_pubs = [y for x in pubs_per_chan for y in x]
        pubs_per_edit = (db.session.query(Publishing).filter((Publishing.channel_id == c.id) &
                                                             (Publishing.state == 66)) for c in chans)
        flattened_list_edit = [y for x in pubs_per_edit for y in x]
        flattened_list_pubs += flattened_list_edit
    return render_template("moderate.html", publishings=flattened_list_pubs)


@pub_page.route('/moderate/unvalidate/<int:id>', methods=["GET", "POST"])
@login_required()
def unvalidate_publishing(id):
    """SAVOIR SI ON FAIT POST_ID ET CHANNEL_ID OU PUBLISHING_ID DIRECTLY"""

    print("pub-id to unvalidate ", id)
    pub = db.session.query(Publishing).filter(Publishing.publishing_id == id).first()
    pub.state = State.REFUSED.value

    """TESTER SI MODERATOR_COMMENT EST NONE"""
    moderator_comment = ""
    print('mod', request.form.get('moderator_comment'))
    if request.form.get('moderator_comment'):
        moderator_comment = request.form.get('moderator_comment')
    print('mod_com', moderator_comment)

    comm = db.session.query(Comment).filter(Comment.publishing_id == pub.publishing_id).first()
    date_moderator_comment = str_converter(datetime_now())
    if comm:
        comm.moderator_comment = moderator_comment
        comm.date_moderator_comment = date_moderator_comment
    else:
        comm = Comment(publishing_id=pub.publishing_id, moderator_comment=moderator_comment,
                       date_moderator_comment=date_moderator_comment)
        db.session.add(comm)

    db.session.commit()
    return redirect(url_for('index'))


def get_post_form_validations():
    mods = get_modules_names(current_app.config["PLUGINS"].keys())
    post_form_validations = dict()
    for m in mods:
        fields = {}
        post_form_validations[m] = fields
    return post_form_validations
