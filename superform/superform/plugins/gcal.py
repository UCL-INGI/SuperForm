import json
from datetime import datetime
from flask import session, redirect, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from superform.models import StatusCode, User
from superform.utils import str_converter, str_time_converter

FIELDS_UNAVAILABLE = ['Image']
PROJECT_ID = 'project_id'
CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secret'
REDIRECT_URIS = 'redirect_uris'
JAVASCRIPT_ORIGINS = 'javascript_origins'
CONFIG_FIELDS = [PROJECT_ID, CLIENT_ID, CLIENT_SECRET, REDIRECT_URIS, JAVASCRIPT_ORIGINS]


def generate_user_credentials(channel_config, id, idc):
    scope = 'https://www.googleapis.com/auth/calendar'
    client_config = get_full_config(json.loads(channel_config))
    flow = Flow.from_client_config(client_config, scopes=scope)
    flow.redirect_uri = url_for('gcal_callback.callback_gc', _external=True)
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true',
        # Ask for the refresh token even if not the first time (otherwise it is not returned)
        prompt='consent')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state
    # Store the concerned publishing so we can immediately redirect to its moderation
    # Store the concerned channel for the same reason and to be able to retrieve the channel's config in the callback
    session['gcal_cb_pub_id'] = id
    session['gcal_cb_channel_id'] = idc

    return redirect(authorization_url)


def get_user_credentials():
    user = User.query.get(session["user_id"])
    if not user or not user.gcal_cred:
        return None
    return Credentials.from_authorized_user_info(json.loads(user.gcal_cred))


def get_full_config(channel_config):
    return {"web": {"client_id": channel_config[CLIENT_ID],
                    "project_id": channel_config[PROJECT_ID],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": channel_config[CLIENT_SECRET],
                    "redirect_uris": [channel_config[REDIRECT_URIS]],
                    "javascript_origins": [channel_config[JAVASCRIPT_ORIGINS]]}}


def generate_event(publishing):
    return {
        'summary': publishing.title,
        'description': publishing.description,
        'attachments': [
            {
                "fileUrl": publishing.link_url,
            }
        ],
        'start': {
            'dateTime': build_full_date_from(publishing),
            'timeZone': 'Europe/Zurich',
        },
        'end': {
            'dateTime': build_full_date_until(publishing),
            'timeZone': 'Europe/Zurich',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }


def build_full_date_from(publishing):
    return str_converter(publishing.date_from) + "T" + str_time_converter(publishing.start_hour) + ':00Z'


def build_full_date_until(publishing):
    return str_converter(publishing.date_until) + "T" + str_time_converter(publishing.end_hour) + ':00Z'


def run(publishing, channel_config):
    creds = get_user_credentials()
    if not creds:
        return StatusCode.ERROR, "Failed to get user credentials."
    if len(publishing.title.strip()) == 0:
        return StatusCode.ERROR, "The title is empty."
    if not timerange_valid(publishing):
        return StatusCode.ERROR, "The specified time range is invalid."
    service = build('calendar', 'v3', credentials=creds)
    event = generate_event(publishing)
    publish(event, service)
    return StatusCode.OK, None


def publish(event, service):
    """
    Publie sur le compte et renvoie l'id de la publication
    """
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event.get('htmlLink')


def delete(id):
    """
    Supprime la publication
    """


def full_datetime_converter(stri):
    return datetime.strptime(stri, "%Y-%m-%dT%H:%M:%SZ")


def timerange_valid(pub):
    # now = datetime.now()
    return full_datetime_converter(build_full_date_from(pub)) <= full_datetime_converter(
        build_full_date_until(pub))
