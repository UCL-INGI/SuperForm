from flask import Blueprint, flash, redirect, render_template, request, url_for
from superform import channels
from superform.models import db, Publishing, Channel, State
from superform.utils import login_required, datetime_converter, str_converter

pub_page = Blueprint('publishings', __name__)


def create_a_publishing(post, chn, form):
    chan = str(chn.name)

    plug_name = chn.module
    from importlib import import_module
    plug = import_module(plug_name)

    if 'forge_link_url' in dir(plug):
        link_post = plug.forge_link_url(chan, form)
    else:
        link_post = form.get(chan + '_linkurlpost') if form.get(chan + '_linkurlpost') is not None else post.link_url

    title_post = form.get(chan + '_titlepost') if (form.get(chan + '_titlepost') is not None) else post.title
    descr_post = form.get(chan + '_descriptionpost') if form.get(
        chan + '_descriptionpost') is not None else post.description
    image_post = form.get(chan + '_imagepost') if form.get(chan + '_imagepost') is not None else post.image_url
    date_from = datetime_converter(form.get(chan + '_datefrompost')) if datetime_converter(
        form.get(chan + '_datefrompost')) is not None else post.date_from
    date_until = datetime_converter(form.get(chan + '_dateuntilpost')) if datetime_converter(
        form.get(chan + '_dateuntilpost')) is not None else post.date_until
    pub = Publishing(post_id=post.id, channel_id=chn.id, state=State.NOTVALIDATED.value, title=title_post, description=descr_post,
                     link_url=link_post, image_url=image_post,
                     date_from=date_from, date_until=date_until)

    db.session.add(pub)
    db.session.commit()
    return pub


@pub_page.route('/moderate/<int:id>/<string:idc>', methods=["GET", "POST"])
@login_required()
def moderate_publishing(id, idc):
    pub = db.session.query(Publishing).filter(Publishing.post_id == id, Publishing.channel_id == idc).first()
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

