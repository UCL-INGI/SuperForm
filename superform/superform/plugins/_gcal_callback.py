import json
from google_auth_oauthlib.flow import Flow
from flask import Blueprint, flash, request, session, url_for, redirect
from superform.models import Channel, db, User
from superform.utils import login_required
from superform.plugins.gcal import get_full_config

gcal_page = Blueprint('gcal_callback', __name__)


@gcal_page.route("/callback_gc", methods=['GET', 'POST'])
@login_required(admin_required=True)
def callback_gc():
    state = session['state']
    id = session['gcal_cb_pub_id']
    idc = session['gcal_cb_channel_id']
    scope = 'https://www.googleapis.com/auth/calendar'
    channel = db.session.query(Channel).filter(Channel.id == idc).first()
    client_config = get_full_config(json.loads(channel.config))
    flow = Flow.from_client_config(client_config, scopes=scope, state=state)

    flow.redirect_uri = url_for('gcal_callback.callback_gc', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    set_user_credentials(creds)
    flash("Gcal credentials saved.", category='success')
    # return redirect(url_for('index'))
    return redirect(url_for("publishings.moderate_publishing", id=id, idc=idc))


def set_user_credentials(creds):
    user = User.query.get(session["user_id"])
    user.gcal_cred = creds_to_string(creds)
    db.session.commit()


def creds_to_string(creds):
    return json.dumps({'token': creds.token,
                       'refresh_token': creds.refresh_token,
                       'token_uri': creds.token_uri,
                       'client_id': creds.client_id,
                       'client_secret': creds.client_secret,
                       'scopes': creds.scopes})
