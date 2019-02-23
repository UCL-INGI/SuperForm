import os
from flask import Blueprint, json, jsonify, request, redirect, render_template, session

from posts import create_a_publishing, pre_validate_post
from superform.utils import login_required, datetime_converter
import json
from superform.models import db, Post, Publishing, Channel, User
from superform.users import channels_available_for_user

from datetime import date, timedelta

# from users import channels_available_for_user

edit_page = Blueprint('edit', __name__)


@edit_page.route('/edit/<int:post_id>', methods=['GET'])
@login_required()
def edit_post(post_id):
    """
    Method called in the home page, when the user clicks on the 'Edit' button on a post.
    Generate the layout of the page, with the fields of the post filled with the values stored in the database.
    :param post_id: The id of the post in the database
    :return: The template of the html edition page
    """
    return render_template('edit.html', post_id=post_id)


@edit_page.route('/edit/publish_edit_post/<int:post_id>', methods=['POST'])
@login_required()
def publish_edit_post(post_id):
    """
    Method called in the edition page, when the user clicks on the 'Save and publish' button.
    It is called with an http post request.
    The method will save the changes to the post fields in the database.
    :param post_id: The id of the post in the database
    :return: An http error/sucess code
    """
    data = request.get_json(force=True)

    current_user_id = session.get("user_id", "")

    post = db.session.query(Post).filter(Post.id == post_id,
                                         Post.user_id == current_user_id).first()  # retrieve old post
    pubs = db.session.query(Publishing).filter(Publishing.post_id == post_id).all()  # retrieve old publishings
    list_of_channels = channels_available_for_user(current_user_id)
    list_of_channels_name = list()
    if post is None:
        return redirect('/403')

    for pub in pubs:
        p = (db.session.query(Channel).filter((Channel.id == pub.channel_id))).first()
        if p in list_of_channels:
            list_of_channels.remove(p)

    for elem in list_of_channels:
        list_of_channels_name.append(elem.name)

    for d in data:  # d is a post/publication
        name = d.get('name')
        fields = d.get('fields')

        if d.get('name') == 'General':
            keys = fields.keys()
            for k in keys:
                if (k == 'date_from') and (fields.get(k) is ''):
                    setattr(post, k, date.today())
                elif (k == 'date_until') and (fields.get(k) is ''):
                    setattr(post, k, date.today() + timedelta(days=7))
                elif k in {'date_from', 'date_until'}:
                    setattr(post, k, datetime_converter(fields.get(k)))
                else:
                    setattr(post, k, fields.get(k))
            db.session.commit()
        elif name in list_of_channels_name:
            for cha in list_of_channels:
                if cha.name == name:
                    create_a_publishing_edit(post, cha, d)
        else:
            for pub in pubs:
                chans = db.session.query(Channel).filter(Channel.id == pub.channel_id).all()
                try:
                    from importlib import import_module
                    chan = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
                    plugin = import_module(chan.module)
                    can_edit = plugin.can_edit(pub, chan.config)
                except AttributeError:
                    can_edit = False
                if pub.state == 1 and can_edit:
                    """
                    We use the state 66 to indicate if a post who is already publish, is edited.
                    Don't use this state for anything else !!!
                    """
                    setattr(pub, 'state', 66)
                for chn in chans:
                    if chn.name == name:
                        keys = fields.keys()
                        for k in keys:
                            if (k == 'date_from') and (fields.get(k) is ''):
                                setattr(pub, k, date.today())
                            elif (k == 'date_until') and (fields.get(k) is ''):
                                setattr(pub, k, date.today() + timedelta(days=7))
                            elif k in {'date_from', 'date_until', 'date_start', 'date_end'}:
                                setattr(pub, k, datetime_converter(fields.get(k)))
                            else:
                                setattr(pub, k, fields.get(k))
                        db.session.commit()

    return ('', 200)


@edit_page.route('/edit/layout/<int:post_id>', methods=['GET'])
@login_required()
def create_data_json(post_id):
    """
    This method is called when loading the edition page.
    It is responsible for getting the post and publication data from the database and encoding it inside a json.
    :param post_id: The id of the post in the database
    :return: The data related to the post/publication, in json format
    """
    current_user_id = session.get("user_id", "")

    json_output = dict()
    dic_second = dict()

    query_post = db.session.query(Post).filter(Post.id == post_id, Post.user_id == current_user_id).first()
    query_pubs = db.session.query(Publishing).filter(Publishing.post_id == post_id).all()
    list_of_channels = channels_available_for_user(current_user_id)

    fields = dict((col, getattr(query_post, col)) for col in query_post.__table__.columns.keys())
    entries_to_delete = ('id', 'user_id', 'date_created')
    for entries in entries_to_delete:
        del fields[entries]

    dic_second["fields"] = fields
    json_output["default"] = dic_second

    module = list()
    for pub in query_pubs:
        channel = dict()
        p = (db.session.query(Channel).filter((Channel.id == pub.channel_id))).first()
        if p in list_of_channels:
            list_of_channels.remove(p)
        try:
            from importlib import import_module
            plugin = import_module(p.module)
            can_edit = plugin.can_edit(pub, p.config)
        except AttributeError:
            can_edit = False
        if not (pub.state == 1 and not can_edit):
            elem = dict((col, getattr(p, col)) for col in p.__table__.columns.keys())
            for e in elem:
                if e == "module" or e == "name":
                    channel[e] = elem[e]
            fields = dict()
            for col in pub.__table__.columns.keys():
                try:
                    val = getattr(pub, col)
                    if col == "state":
                        channel[col] = val
                    elif not col == "post_id" and not col == "channel_id":
                        fields[col] = val
                except AttributeError as error:
                    pass
            channel["fields"] = fields
            module.append(channel)

    for chan in list_of_channels:
        channel = dict()
        channel["name"] = chan.name
        channel["module"] = chan.module
        channel["state"] = -1
        module.append(channel)

    json_output["channels"] = module
    return jsonify(json_output)


def create_a_publishing_edit(post, chn, data):
    """
    This method is used in publish_edit_post in order to generate a publication.
    Since the request used in publish_edit_post is different than the request in create_a_publishing in post.py, this
    methode had the same behaviour but instead of using a request.form we use a request.get_json
    :param post : the post linked to the publication, chn : the channel used for the publication, data : data used to
    make the publishing
    :return: the publishing
    """
    validate = pre_validate_post(chn, post)
    if validate == -1 or validate == 0:
        return validate

    field = data.get('fields')
    title_post = field.get('title') if (field.get('title') is not None) else post.title
    descr_post = field.get('description') if field.get('description') is not None else post.description
    link_post = field.get('link_url') if field.get('link_url') is not None else post.link_url
    image_post = field.get('image_url') if field.get('image_url') is not None else post.image_url

    if field.get('date_from') is '':
        date_from = date.today()
    else:
        date_from = datetime_converter(field.get('date_from')) if datetime_converter(
            field.get('date_from')) is not None else post.date_from
    if field.get('date_until') is '':
        date_until = date.today() + timedelta(days=7)
    else:
        date_until = datetime_converter(field.get('date_until')) if datetime_converter(
            field.get('date_until')) is not None else post.date_until
    if chn.module == 'superform.plugins.ICTV':
        logo = field.get('logo')
        subtitle = field.get('subtitle')
        duration = field.get('duration')

        pub = Publishing(post_id=post.id, channel_id=chn.id, state=0, title=title_post, description=descr_post,
                         link_url=link_post, image_url=image_post,
                         date_from=date_from, date_until=date_until, logo=logo, subtitle=subtitle, duration=duration)
    else:
        pub = Publishing(post_id=post.id, channel_id=chn.id, state=0, title=title_post, description=descr_post,
                         link_url=link_post, image_url=image_post,
                         date_from=date_from, date_until=date_until)

    db.session.add(pub)
    db.session.commit()
    return pub
