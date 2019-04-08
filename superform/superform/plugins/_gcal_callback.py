import json
from google_auth_oauthlib.flow import Flow
from flask import Blueprint, flash, request, session, url_for, redirect
from superform.models import db, User
from superform.utils import login_required

gcal_page = Blueprint('gcal_callback', __name__)


@gcal_page.route("/callback_gc", methods=['GET', 'POST'])
@login_required(admin_required=True)
def callback_gc():
    state = session['state']
    scope = 'https://www.googleapis.com/auth/calendar'
    channel_config = get_full_config()
    flow = Flow.from_client_config(channel_config, scopes=scope, state=state)

    flow.redirect_uri = url_for('gcal_callback.callback_gc', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    set_user_credentials(creds)
    flash("Gcal credentials saved.", category='success')
    return redirect(url_for("index"))


def get_full_config():
    return {"web": {"client_id": "444134070785-m1oq8vmcbmkblej8prp2tuo036oasaim.apps.googleusercontent.com",
                    "project_id": "superform-232211", "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "q7R6LdbzsaWwUU9XdaQRcZjY",
                    "redirect_uris": ["https://tfe-lezaack.info.ucl.ac.be/callback_gc"],
                    "javascript_origins": ["https://tfe-lezaack.info.ucl.ac.be"]}}


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
