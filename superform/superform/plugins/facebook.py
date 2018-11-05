from flask import current_app
import json
import facebook

FIELDS_UNAVAILABLE = ['Title', 'Description']  # list of field names that are not used by your module

CONFIG_FIELDS = ["page_id",
                 "app_id"]  # This lets the manager of your module enter data that are used to communicate with other services.


def run(publishing, channel_config):  # publishing:DB channelconfig:DB channel
    """
    page_access_token = "EAAEg6h9DvQwBAKlNUhF4NGa69OYGlgLJZAZBFDZBbZAk0gFScTX2f0EG0ZAkaiVPEWlRBXePLXgy2d8rnE21GI7Ru4mvZAJ8STI0xIaVN0jOGH5xCE6MIIBr3l9jNQVUSo8XafSdZC6KzomTnMiFGcFsGZB7xaGZChZBpL4VJgpnaC2b8fRQltnmZA91qXXlc6gcdcvZB7DF4ZAeWkhAMuVDY9hlJ"
    api = facebook.GraphAPI(access_token=page_access_token)
    msg = "penis"

    api.put_object(
        parent_object="me",
        connection_name="feed",
        message=msg,
        link=""
    )
    """

    page_id = get_page_id(channel_config)
    app_id = get_app_id(channel_config)

    cfg = get_config(page_id, app_id)

    # login le user todo

    # publie sur page possedée par cet user
    #api1 = facebook.GraphAPI(access_token="trouvée au dessus")
    api1 = facebook.GraphAPI(access_token="EAAEg6h9DvQwBALKixA48eCqk6G7baxSzZBkBVcdifTra4FqhJlasQfxKzKrVuZCLEZCSjHGLhoMukcbmHTcOZCwTZBXLzUBeEdDYctuDsAPN9svmPIsTmJlnPE6akX5dPzEJLHPg7N6ZAZCofARAuiPIZAt2zea0SFI5XZBhegA6boAogk9YZBzFXKrk4zbzV3GwzvqZA9RqqoCaWoHR5o7qG74xsRiTEXaXj0ZD")
    response = api1.request('/me/accounts?type=page')  # recoit liste des pages gérée par le user et leurs page tokens
    pages = json.loads(response)
    for page in pages['data']:
        print(page["access_token"])

    api = -1
"""
    msg = get_message(publishing)
    link = get_link(publishing)
    image = get_image(publishing)

    status = api.put_object(
        parent_object="me",
        connection_name="feed",
        message=msg,
        link=link
    )
"""




"""
def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])
    return graph
"""

def get_page_id(config):
    json_data = json.loads(config)
    return json_data['page_id']


def get_app_id(config):
    json_data = json.loads(config)
    return json_data['app_id']


def get_config(page_id, app_id):
    cfg = {
        "page_id": page_id,  # Step 1
        "app_id": app_id  # Step 3
    }
    return cfg


def get_message(publishing):
    return publishing.title + "\n\n" + publishing.description


def get_link(publishing):
    return publishing.link_url


def get_image(publishing):
    return publishing.image_url
