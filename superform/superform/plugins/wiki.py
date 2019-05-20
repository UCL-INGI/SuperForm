import json
import requests
import time
import datetime
import math
from superform.models import StatusCode

# liens utiles :
# urlwiki = "http://localhost/pmwiki-2.2.109/pmwiki.php"
# urlwiki = "http://lezaack-wiki.info.ucl.ac.be/"
#
# à propos de python et des requêtes http :
# http://dridk.me/python-requests.html
# http://docs.python-requests.org/en/master/api/ --> API de requests

# à propos de l'authentification sur pmwiki
# https://www.pmwiki.org/wiki/PmWiki/Passwords

# éditer une page sur wiki :
# https://www.pmwiki.org/wiki/PmWiki/BasicEditing

# COMMENT ON A GERE L'AUTHENTIFICATION POUR LE MOMENT :
# On modifie les accès de notre server local pour que seules les personnes
# possédant le mot de passe puissent créer un nouveau post.
#
#       * Modifier accès server local :
#           --> http://localhost/pmwiki-2.2.109/pmwiki.php?n=News.GroupAttributes?action=attr
#           --> mettre un mot de passe pour le champ edit (par exemple "edit")
#               Dans cet exemple, il y aura donc besoin du mot de passe pour créer toutes les pages qui commencent par News. (ex: News.Conference)
#       * Configurer pmwiki pour qui'il accepte le codage utf-8 :
#               When you first install PmWiki, the local/config.php file does not exist.
#               Copy the sample-config.php file (in the docs/ directory) to local/config.php and use it as a starting point.
#       * Configurer la channel wiki sur superform :
#           --> mettre le mot de passe choisi dans le champ password. Pour l'instant on peut mettre ce qu'on veut dans le champs username

FIELDS_UNAVAILABLE = []
CONFIG_FIELDS = ["url", "username", "password"]


def makeText(publishing, authid):
    text = ""
    # title
    titre = "!! " + publishing.title + "\n"
    text = titre

    # author and date
    try:
        author = authid
    except AttributeError:
        author = "Superform"
    except TypeError:
        author = "Superform"

    date = str(datetime.datetime.now().strftime("%d/%m/%Y"))
    footer = "Par " + str(author) + " Publié le " + date + "\n"
    text = text + footer + "\n" + "-----" + "\n"

    # description
    # corps = str(publishing.description).replace("\n","[[<<]] ") +"\n"
    corps = str(publishing.description).replace("\n", "[[<<]] \n") + "\n"
    text = text + corps + "\n"

    # link
    if len(str(publishing.link_url)) > 0:
        link_url = "-----" + "[[" + publishing.link_url + "]]" + "\n"
        text = text + link_url
    # image
    if (len(str(publishing.image_url))) > 0:
        image_url = "-----" + "\n" + publishing.image_url + "\n"
        text = text + image_url

    text.encode("UTF-8")

    return text


def run(publishing, channel_config):
    json_data = json.loads(channel_config)  # Get the config
    authid = json_data['username']
    authpw = json_data['password']
    urlwiki = json_data['url']
    pageName = "News." + format_title(str(publishing.title))
    text = makeText(publishing, authid)
    data = {"n": pageName, "text": text, "action": "edit", "post": "1", 'authid': authid, "authpw": authpw,
            "basetime": math.floor(time.time())}
    try:
        response = requests.post(urlwiki, data)
    except requests.exceptions.ConnectionError:
        return StatusCode.ERROR, "Couldn't connect to server"
    except requests.exceptions.MissingSchema:
        return StatusCode.ERROR, "Wrong base_url, please check the format again"
    if response.status_code != 200:
        return StatusCode.ERROR, "PmWiki couldn't process your request. The new was not published."
    return StatusCode.OK, response


def format_title(title):
    """
    Format the title to fit the url
    :param title: title
    :return: formatted title
    """
    import re
    delimiters = "-", " ", ",", ";", ".", "\\", "/", "<", ">", "@", "?", "=", "+", "%", "*", "`", "\"", "\n", "&", "#", "_"
    pattern = '|'.join(map(re.escape, delimiters))
    split = re.split(pattern, title)
    formatted_title = ""
    for m in split:
        formatted_title += m

    return formatted_title
