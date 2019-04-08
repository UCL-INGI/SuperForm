import json

from datetime import date, timedelta
from flask import Blueprint, current_app, flash, url_for, request, redirect, session, render_template
from importlib import import_module

from superform.plugins import gcal
from superform.channels import valid_conf
from superform.models import db, User, Publishing, Channel, Comment, State, AlchemyEncoder, StatusCode
from superform.users import get_moderate_channels_for_user
from superform.utils import login_required, datetime_converter, str_converter, datetime_now, get_modules_names, \
    str_converter_with_hour, time_converter, str_time_converter

pub_page = Blueprint('publishings', __name__)


def create_a_publishing(post, chn, form):  # called in publish_from_new_post()
    chan = str(chn.name)
    plug = import_module(chn.module)
    title_post = form.get(chan + '_titlepost') if (form.get(chan + '_titlepost') is not None) else post.title
    # Team2 stat
    chn.count += 1
    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    # Team2 stat

    # TEAM 10 twitter
    if "twitter" in chn.module:
        descr_post = form.get('tweets')
    elif form.get(chan + '_descriptionpost') is not None:
        descr_post = form.get(chan + '_descriptionpost')
    else:
        descr_post = post.description
    # TEAM 10 twitter

    # TEAM 3 ictv
    if 'forge_link_url' in dir(plug):
        link_post = plug.forge_link_url(chan, form)
    else:
        link_post = form.get(chan + '_linkurlpost') if form.get(
            chan + '_linkurlpost') is not None else post.link_url
    # TEAM 3 ictv

    image_post = form.get(chan + '_imagepost') if form.get(chan + '_imagepost') is not None else post.image_url

    if form.get(chan + 'datefrompost') is '':
        date_from = date.today()
    else:
        date_from = datetime_converter(form.get(chan + '_datefrompost')) if form.get(
            chan + '_datefrompost') is not None else post.date_from
    if form.get(chan + 'dateuntilpost') is '':
        date_until = date.today() + timedelta(days=7)
    else:
        date_until = datetime_converter(form.get(chan + '_dateuntilpost')) if form.get(
            chan + '_datefrompost') is not None else post.date_until

    if form.get(chan + 'starthour') is '':
        start_hour = time_converter("00:00")
    else:
        start_hour = time_converter(form.get(chan + '_starthour')) if form.get(
            chan + '_start_hour') is not None else post.start_hour
    if form.get(chan + 'dateuntilpost') is '':
        end_hour = time_converter("23:59")
    else:
        end_hour = time_converter(form.get(chan + '_endhour')) if form.get(
            chan + '_endhour') is not None else post.end_hour

    latest_version_publishing = db.session.query(Publishing).filter(Publishing.post_id == post.id,
                                                                    Publishing.channel_id == chn.id).order_by(
        Publishing.num_version.desc()).first()
    version_number = 1 if latest_version_publishing is None else latest_version_publishing.num_version + 1

    pub = Publishing(num_version=version_number, post_id=post.id, user_id=user_id, channel_id=chn.id,
                     state=State.NOT_VALIDATED.value, title=title_post, description=descr_post,
                     link_url=link_post, image_url=image_post,
                     date_from=date_from, date_until=date_until, start_hour=start_hour, end_hour=end_hour)

    # TEAM6: MODIFICATION FOR PDF
    c = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
    if c is not None:
        plugin_name = c.module
        # If it is a pdf chanel we don't need to save it, printing it would be enough
        if str(plugin_name).endswith("pdf"):
            c_conf = c.config
            plugin = import_module(plugin_name)
            plugin.run(pub, c_conf)
            # Does not save the pdf posts
            return pub
    # TEAM6: END OF MODIFICATION

    db.session.add(pub)
    db.session.commit()

    if latest_version_publishing is None:
        user_comment = ""
        date_user_comment = str_converter_with_hour(datetime_now())
        comm = Comment(publishing_id=pub.publishing_id, user_comment=user_comment,
                       date_user_comment=date_user_comment)
        db.session.add(comm)
        db.session.commit()

    return pub


@pub_page.route('/moderate/<int:id>/<string:idc>', methods=["GET", "POST"])
@login_required()
def moderate_publishing(id, idc):
    pub = db.session.query(Publishing).filter(Publishing.post_id == id, Publishing.channel_id == idc).order_by(
        Publishing.num_version.desc()).first()
    if pub.state != State.NOT_VALIDATED.value:
        flash("This publication has already been moderated", category='info')
        return redirect(url_for('index'))

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
    pub.date_from = str_converter(pub.date_from)
    pub.date_until = str_converter(pub.date_until)
    pub.start_hour = str_time_converter(pub.start_hour)
    pub.end_hour = str_time_converter(pub.end_hour)

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
        pub.start_hour = time_converter(request.form.get('starthour')) if request.form.get(
            'starthour') is not None else time_converter("00:00")
        pub.end_hour = time_converter(request.form.get('endhour')) if request.form.get(
            'endhour') is not None else time_converter("23:59")

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
            # try to run the plugin
            try:
                plug_exitcode = plugin.run(pub, c_conf)
            except Exception as e:
                # unexpected exception
                flash("An unexpected error occurred while publishing, please contact an admin.", category='error')
                import sys
                print(str(e), file=sys.stderr)
                return redirect(url_for('publishings.moderate_publishing', id=id, idc=idc))

            if type(plug_exitcode) is tuple and len(plug_exitcode) >= 2 and plug_exitcode[
                0].value == StatusCode.ERROR.value:
                # well known exception
                flash(plug_exitcode[1], category='error')
                return redirect(url_for('publishings.moderate_publishing', id=id, idc=idc))
            if type(plug_exitcode) is tuple and len(plug_exitcode) >= 2 and plug_exitcode[
                0].value == StatusCode.URL.value:
                # redirect URL
                return plug_exitcode[1]

            # If we reach here, the publication was successfull
            pub.state = 1
            db.session.commit()
            flash("The publishing has successfully been published.", category='success')

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
    date_moderator_comment = str_converter_with_hour(datetime_now())
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
