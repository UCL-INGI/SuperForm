from flask import url_for, current_app, Blueprint, request, redirect
from superform.utils import login_required
from superform.models import db, Channel
import requests

linkedin_page = Blueprint('linkedin_callback', __name__)


@linkedin_page.route("/callback_In", methods=['GET', 'POST'])
@login_required(admin_required=True)
def callback_In():
    """Page where LinkedIn returns the code to get the access token.
            Generate the access token from the code and save it to the DB."""
    id_channel = request.args.get('state')
    if id_channel is None:
        return redirect(url_for("channels.channel_list"))
    app_key = current_app.config["LINKEDIN_API_KEY"]
    app_secret = current_app.config["LINKEDIN_API_SECRET"]
    code = request.args.get('code')
    if "error" in request.args:
        error = request.args.get('error')
    canvas_url = url_for('linkedin_callback.callback_In', _external=True)
    try:
        response = requests.post("https://www.linkedin.com/oauth/v2/accessToken",
                                 data={"grant_type": "authorization_code", "code": code, "redirect_uri": canvas_url,
                                       "client_id": app_key, "client_secret": app_secret})
        response = response.json()
        token = response['access_token']
    except Exception:
        token = 'Unable to generate access_token'

    channel = Channel.query.get(id_channel)
    if channel == None or channel.module != 'superform.plugins.linkedin':
        return redirect(url_for("channels.channel_list"))
    # reset config and add new access_token
    channel.config = "{\"access_token\": \"" + str(token) + "\"}"

    db.session.commit()
    return redirect(url_for("channels.configure_channel", id=id_channel))
