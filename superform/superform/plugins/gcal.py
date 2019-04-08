import google_auth_oauthlib
from flask import session, redirect, url_for
from superform.models import db, User, StatusCode
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from superform.utils import str_converter, str_time_converter
import json

FIELDS_UNAVAILABLE = ['Image']
PROJECT_ID = 'project_id'
CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secret'
CONFIG_FIELDS = [PROJECT_ID, CLIENT_ID, CLIENT_SECRET]


# def generate_user_credentials(channel_config, user_id=None):
#     creds = get_user_credentials(user_id)
#     if not creds:
#         scope = 'https://www.googleapis.com/auth/calendar'
#         channel_config = get_full_config(json.loads(channel_config))
#         flow = Flow.from_client_config(channel_config, scopes=scope)
#         flow.redirect_uri = url_for('gcal_callback.callback_gc', _external=True)
#         authorization_url, state = flow.authorization_url(
#             # Enable offline access so that you can refresh an access token without
#             # re-prompting the user for permission. Recommended for web server apps.
#             access_type='offline',
#             # Enable incremental authorization. Recommended as a best practice.
#             include_granted_scopes='true')
#
#         # Store the state so the callback can verify the auth server response.
#         session['state'] = state
#
#         return redirect(authorization_url)
#
#         # creds = flow.run_local_server(host='localhost', port=8080,
#         #                               authorization_prompt_message='Please visit this URL: {url}',
#         #                               success_message='The auth flow is complete, you may close this window.',
#         #                               open_browser=True)
#         # set_user_credentials(creds, user_id)


def get_user_credentials(user_id=None):
    user = User.query.get(user_id) if user_id else User.query.get(session["user_id"])
    return Credentials.from_authorized_user_info(json.loads(user.gcal_cred)) if user.gcal_cred else None


def get_full_config(channel_config):
    return {"web": {"client_id": "444134070785-m1oq8vmcbmkblej8prp2tuo036oasaim.apps.googleusercontent.com",
                    "project_id": "superform-232211", "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_secret": "q7R6LdbzsaWwUU9XdaQRcZjY",
                    "redirect_uris": ["https://tfe-lezaack.info.ucl.ac.be/callback_gc"],
                    "javascript_origins": ["https://tfe-lezaack.info.ucl.ac.be"]}}

# def get_full_config(channel_config):
#     return {"web": {"client_id": channel_config[CLIENT_ID],
#                     "project_id": channel_config[PROJECT_ID],
#                     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                     "token_uri": "https://oauth2.googleapis.com/token",
#                     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#                     "client_secret": channel_config[CLIENT_SECRET],
#                     "redirect_uris": ["https://tfe-lezaack.info.ucl.ac.be/callback_gc/"],
#                     "javascript_origins": ["https://tfe-lezaack.info.ucl.ac.be"]}}


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
    creds = get_user_credentials(publishing.user_id)
    if not creds:
        scope = 'https://www.googleapis.com/auth/calendar'
        channel_config = get_full_config(json.loads(channel_config))
        flow = Flow.from_client_config(channel_config, scopes=scope)
        flow.redirect_uri = url_for('gcal_callback.callback_gc', _external=True)
        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',
            # Ask for the refresh token even if not the first time (otherwise not returned)
            prompt='consent')

        # Store the state so the callback can verify the auth server response.
        session['state'] = state

        return StatusCode.URL, redirect(authorization_url)
    if len(publishing.title.strip()) == 0:
        return StatusCode.ERROR, "Bad Title"
    if not timerange_valid(publishing):
        return StatusCode.ERROR, "The specified time range is empty."
    service = build('calendar', 'v3', credentials=creds)
    event = generate_event(publishing)
    id = publish(event, service)
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
    # must have a date_from / date_until with hour and date
    now = datetime.now()
    return now <= full_datetime_converter(build_full_date_from(pub)) <= full_datetime_converter(
        build_full_date_until(pub))
