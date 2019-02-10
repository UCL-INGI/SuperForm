import facebook

from flask import url_for, current_app, Blueprint, request, redirect
from superform.utils import login_required
from superform.models import db, Channel

facebook_page = Blueprint('facebook_callback', __name__)

@facebook_page.route("/callback_fb", methods=['GET', 'POST'])
@login_required(admin_required=True)
def callback_fb():
    """Page where Facebook returns the code to get the access token.
        Generate the access token from the code and save it to the DB."""
    id_channel = request.args.get('state')
    code = request.args.get('code')
    if id_channel is None:
        return redirect(url_for("channels.channel_list"))

    app_id = current_app.config["FACEBOOK_APP_ID"]
    app_secret = current_app.config["FACEBOOK_APP_SECRET"]
    canvas_url = url_for('facebook_callback.callback_fb', _external=True)
    graph = facebook.GraphAPI()
    try:
        res = graph.get_access_token_from_code(code, canvas_url, app_id, app_secret)
        access_token = res['access_token']
    except facebook.GraphAPIError:
        access_token = 'Unable to generate access_token'

    channel = Channel.query.get(id_channel)
    if channel == None or channel.module != 'superform.plugins.facebook':
        return redirect(url_for("channels.channel_list"))
    # reset config and add new access_token
    channel.config = "{\"access_token\": \"" + str(access_token) + "\"}"

    db.session.commit()
    return redirect(url_for("channels.configure_channel", id=id_channel))