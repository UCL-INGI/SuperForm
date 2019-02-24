import json

from datetime import date, timedelta
from flask import Blueprint, url_for, request, redirect, session, render_template
from importlib import import_module

from plugins import gcal_plugin
from superform.utils import login_required, datetime_converter, str_converter, datetime_now
from superform.models import db, User, Publishing, Channel, Comment, State, AlchemyEncoder
from superform.users import get_moderate_channels_for_user
from superform.posts import get_post_form_validations

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
        pub = Publishing(num_version=latest_version_publishing.num_version + 1, post_id=post.id, channel_id=chn.id,
                         state=State.NOT_VALIDATED.value, title=title_post, description=descr_post,
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
    pub = db.session.query(Publishing).filter(Publishing.post_id == id, Publishing.channel_id == idc).first()

    # Only publishing that have yet to be moderated can be viewed
    if pub.state != 0:
        flash("This publication has already been moderated", category='info')
        return redirect(url_for('index'))

    c = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
    pub.date_from = str_converter(pub.date_from)
    pub.date_until = str_converter(pub.date_until)

    plugin_name = c.module
    c_conf = c.config
    from importlib import import_module
    plugin = import_module(plugin_name)

    if request.method == "GET":
        if channels.valid_conf(c_conf, plugin.CONFIG_FIELDS):
            return render_template('moderate_post.html', pub=pub, notconf=False)
        else:
            return render_template('moderate_post.html', pub=pub, notconf=True)
    else:
        pub.title = request.form.get('titlepost')
        pub.description = request.form.get('descrpost')
        pub.link_url = request.form.get('linkurlpost')
        pub.image_url = request.form.get('imagepost')
        pub.date_from = datetime_converter(request.form.get('datefrompost'))
        pub.date_until = datetime_converter(request.form.get('dateuntilpost'))

        if channels.valid_conf(c_conf, plugin.CONFIG_FIELDS):
            # state is shared & validated
            pub.state = 1
            db.session.commit()
            # running the plugin here
            plugin.run(pub, c_conf)
        else:
            return render_template('moderate_post.html', pub=pub, notconf=True)

        return redirect(url_for('index'))
