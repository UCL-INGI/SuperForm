import json

from flask import Blueprint, current_app, url_for, request, redirect, render_template

from superform.utils import login_required, get_instance_from_module_path, get_modules_names, get_module_full_name
from superform.models import db, Channel
import ast

channels_page = Blueprint('channels', __name__)


def valid_conf(config, fields):
    config_json = json.loads(config)
    for field in fields:
        if field not in config_json:
            return False
    return True


@channels_page.route("/channels", methods=['GET', 'POST'])
@login_required(admin_required=True)
def channel_list():
    if request.method == "POST":
        action = request.form.get('@action', '')
        if action == "new":
            name = request.form.get('name')
            module = request.form.get('module')
            if module in get_modules_names(current_app.config["PLUGINS"].keys()):
                channel = Channel(name=name, module=get_module_full_name(module), config="{}")
                db.session.add(channel)
                db.session.commit()
        elif action == "delete":
            channel_id = request.form.get("id")
            channel = Channel.query.get(channel_id)
            if channel:
                db.session.delete(channel)
                db.session.commit()
        elif action == "edit":
            channel_id = request.form.get("id")
            channel = Channel.query.get(channel_id)
            name = request.form.get('name')
            channel.name = name
            db.session.commit()

    channels = Channel.query.all()
    return render_template("channels.html", channels=channels,
                           modules=get_modules_names(current_app.config["PLUGINS"].keys()))


@channels_page.route("/configure/<int:id>", methods=['GET', 'POST'])
@login_required(admin_required=True)
def configure_channel(id):
    c = Channel.query.get(id)
    m = c.module
    clas = get_instance_from_module_path(m)
    config_fields = clas.CONFIG_FIELDS

    if request.method == 'GET':
        if c.config is not "":
            d = ast.literal_eval(c.config)
            setattr(c, "config_dict", d)
        return render_template("channel_configure.html", channel=c, config_fields=config_fields)

    cfg = {}
    for field in config_fields:
        cfg[field] = request.form.get(field)
    c.config = json.dumps(cfg)

    db.session.commit()
    return redirect(url_for('channels.channel_list'))
