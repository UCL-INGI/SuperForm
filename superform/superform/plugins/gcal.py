from flask import session
from superform.models import db, User, StatusCode
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from superform.utils import str_converter, str_time_converter, datetime_converter
import json

FIELDS_UNAVAILABLE = ['Image']
PROJECT_ID = 'project_id'
CLIENT_ID = 'client_id'
CLIENT_SECRET = 'client_secret'
CONFIG_FIELDS = [PROJECT_ID, CLIENT_ID, CLIENT_SECRET]


def creds_to_string(creds):
    return json.dumps({'token': creds.token,
                       'refresh_token': creds._refresh_token,
                       'token_uri': creds._token_uri,
                       'client_id': creds._client_id,
                       'client_secret': creds._client_secret,
                       'scopes': creds._scopes})


def generate_user_credentials(channel_config, user_id=None):
    SCOPES = 'https://www.googleapis.com/auth/calendar'

    creds = get_user_credentials(user_id)
    if not creds:
        channel_config = get_full_config(json.loads(channel_config))
        flow = InstalledAppFlow.from_client_config(channel_config, scopes=[SCOPES])
        creds = flow.run_local_server(host='localhost', port=8080,
                                      authorization_prompt_message='Please visit this URL: {url}',
                                      success_message='The auth flow is complete, you may close this window.',
                                      open_browser=True)
        set_user_credentials(creds, user_id)


def get_user_credentials(user_id=None):
    user = User.query.get(user_id) if user_id else User.query.get(session["user_id"])
    return Credentials.from_authorized_user_info(json.loads(user.gcal_cred)) if user.gcal_cred else None


def set_user_credentials(creds, user_id=None):
    user = User.query.get(user_id) if user_id else User.query.get(session["user_id"])
    user.gcal_cred = creds_to_string(creds)
    db.session.commit()


def get_full_config(channel_config):
    return {"installed": {"client_id": channel_config[CLIENT_ID],
                          "project_id": channel_config[PROJECT_ID],
                          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                          "token_uri": "https://www.googleapis.com/oauth2/v3/token",
                          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                          "client_secret": channel_config[CLIENT_SECRET],
                          "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]}}


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
        return StatusCode.ERROR, "Failed to get credentials"
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
