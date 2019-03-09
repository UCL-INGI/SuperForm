import facebook
import json

from flask import url_for, current_app, render_template

from models import StatusCode

FIELDS_UNAVAILABLE = ['Title']

CONFIG_FIELDS = ["access_token", "page"]


def render_specific_config_page(c, config_fields):
    """Render a specific template to configure a Facebook channel"""
    return render_template("channel_configure_facebook.html", channel=c, config_fields=config_fields,
                           url_token=get_url_for_token(c.id),
                           pages=get_list_user_pages(c.config_dict.get("access_token")))


def run(publishing, channel_config):
    """Publish the post on the selected page on Facebook"""
    json_data = json.loads(channel_config)
    acc_tok = json_data['access_token']
    if 'page' not in json_data:
        return StatusCode.ERROR, "Invalid page"
    page_id = json_data['page']
    page = get_page_from_id(acc_tok, page_id)
    if page is None:
        return StatusCode.ERROR, "Invalid page ID"
    try:
        graph = facebook.GraphAPI(access_token=page['access_token'])
        # check token validity
        debug = graph.debug_access_token(
            page['access_token'],
            current_app.config["FACEBOOK_APP_ID"],
            current_app.config["FACEBOOK_APP_SECRET"])
        if not debug['data']['is_valid']:
            return StatusCode.ERROR, "Invalid Access-Token"
        # publish post
        graph.put_object(
            parent_object="me",
            connection_name="feed",
            message=publishing.description,
            link=publishing.link_url)
    except facebook.GraphAPIError:
        return StatusCode.ERROR, "GraphAPIError"
    return StatusCode.OK, None


def check_validity(channel_config):
    """ Test validity of the channel. Return an error message if any. """
    json_data = json.loads(channel_config)
    acc_tok = json_data['access_token']
    if 'page' not in json_data:
        return "Error : Invalid page."
    page_id = json_data['page']
    page = get_page_from_id(acc_tok, page_id)
    if page is None:
        return "Error : Invalid page ID."
    try:
        graph = facebook.GraphAPI(access_token=page['access_token'])
        # check token validity
        debug = graph.debug_access_token(
            page['access_token'],
            current_app.config["FACEBOOK_APP_ID"],
            current_app.config["FACEBOOK_APP_SECRET"])
        if not debug['data']['is_valid']:
            return "Error : Invalid Access-Token."
    except facebook.GraphAPIError:
        return "Error : GraphAPIError."


def get_url_for_token(id_channel):
    """Return an URL to Facebook to get a valid access token."""
    app_id = current_app.config["FACEBOOK_APP_ID"]
    canvas_url = url_for('facebook_callback.callback_fb', _external=True)
    perms = ["manage_pages", "publish_pages"]
    graph = facebook.GraphAPI()
    url = graph.get_auth_url(app_id, canvas_url, perms)
    return url + "&state=" + str(id_channel)


def get_list_user_pages(acc_tok):
    """Return a list of dictionaries representing the Facebook pages of the user."""
    try:
        graph = facebook.GraphAPI(access_token=acc_tok)
        pages = graph.get_object('me/accounts')
        return pages['data']
    except facebook.GraphAPIError:
        return [{'id': '0', 'name': 'Unable to load user pages'}]


def get_page_from_id(acc_tok, page_id):
    """Return the dictionary corresponding to the page with id page_id"""
    if page_id == 0:
        return None
    try:
        graph = facebook.GraphAPI(access_token=acc_tok)
        pages = graph.get_object('me/accounts')
        for page in pages['data']:
            if page['id'] == page_id:
                return page
        return None
    except facebook.GraphAPIError:
        return None
