import json
from requests import get, post, exceptions
import datetime
from time import time

from models import StatusCode

FIELDS_UNAVAILABLE = ['ictv_data_form']

CONFIG_FIELDS = ['ictv_server_fqdn', 'ictv_channel_id', 'ictv_api_key']


class IctvException(Exception):
    """
    This class is the superclass that represents the errors from the ICTV plugin
    """
    msg = ''

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    def popup(self):
        """
        Generate HTML code for ICTV error messages
        :return: the encapsulation of the error message
        """
        txt = ''
        txt += '<div class="alert alert-danger">\n'
        txt += '\t<strong>ERROR</strong>\n' + self.msg + '\n'
        txt += '</div>\n'
        return txt


class IctvServerConnection(IctvException):
    """
    This class represents the connection problems toward the remote ICTV server
    """

    def __init__(self, error_code, **kwargs):
        client_msg = ''
        if 'msg' in kwargs:
            client_msg = kwargs['msg']
        self.msg = ''
        if error_code == 403:
            self.msg += '<p>Superform cannot contact the ICTV server !</p>\n\n'
            self.msg += '<p>Please, check the following points :\n' \
                        '\t* Is the channel id given in the configuration the one from the ICTV server ?\n' \
                        '\t* Is the REST API enabled on the channel of the ICTV server ?\n' \
                        '\t* Are the API keys matching ?\n</p>'
        elif error_code == 400:
            self.msg += '<p>The ' + client_msg + ' was misformed. Please correct the data and retry.</p>\n' \
                                                 '<p>If the error persists, take contact with an administrator.</p>'
        elif error_code == 404:
            if client_msg == 'slide':
                self.msg += '<p>The capsule for the slide was not found on the server.</p>'
            else:
                self.msg += '<p>The ictv server is unaccessible. The requests toward the server fails.</p>\n' \
                            '<p>Superform cannot ask the different slides layouts ...</p>'


class IctvChannelConfiguration(IctvException):
    """
    This class represents the configuration problems of the superform ictv plugin
    """

    def __init__(self, fields):
        self.msg = '<p>The following configuration fields of the <strong>' + fields[-1] + \
                   '</strong> channel are misconfigured : </p>\n\t<ul>'
        for i in fields[0:-1]:
            self.msg = self.msg + '\t<li>' + i + '</li>\n'

        self.msg = self.msg + '\t</ul>\n<p>You wont be able to submit your post on this channel !</p>\n<p>Please, ' \
                              'refer to the channel administrator.</p>\n'


# TODO : more interesting to have "plugins manager" in core application to check the configuration
def check_ictv_channel_config(chan_name, chan_config):
    """
    Check if the ictv channel is properly configured
    :param chan_name: the channel name having ictv as plugin
    :param chan_config:
    :raise IctvChannelConfiguration: if the channel is misconfigured
    """
    json_data = json.loads(chan_config)
    missing_fields = [i for i in CONFIG_FIELDS if (i not in json_data or json_data[i] == 'None')]
    if len(missing_fields) != 0:
        missing_fields.append(chan_name)
        raise IctvChannelConfiguration(missing_fields)
    else:
        return json_data


def build_ictv_server_request_args(chan_name, chan_config, method):
    """
    Return the headers required to communicate with the ICTV server given the channel configuration and the type of
    request
    :param chan_name: the name of the channel having ictv as plugin
    :param chan_config: the configuration of the channel
    :param method: the method of the HTTP request
    :return: a dict with the headers of the method of the HTTP request and the url of the channel of the ICTV server
    :raise: IctvChannelConfiguration if the channel is misconfigured
    """
    json_data = check_ictv_channel_config(chan_name, chan_config)

    base_url = 'http://' + json_data['ictv_server_fqdn'] + '/channels/' + json_data['ictv_channel_id'] + '/api'
    headers = {'accept': 'application/json', 'X-ICTV-editor-API-Key': json_data['ictv_api_key']}
    if method == 'POST':
        headers['Content-Type'] = 'application/json'
    return {'url': base_url, 'headers': headers}


def get_ictv_templates(chan_name, chan_config):
    """
    Request the dict of the different slides layout used by the ICTV server
    :param chan_name: the name of the channel having ictv as plugin
    :param chan_config: the configuration of the channel
    :return: the dict of the slides layout
    :raise IctvChannelConfiguration: if the channel is misconfigured
    :raise IctvServerConnection: if the server is not accessible or if the given configuration does not match any
    channels on the ICTV server
    """
    from re import sub
    """ Raise IctvChannelConfiguration if the channel is misconfigured """
    request_args = build_ictv_server_request_args(chan_name, chan_config, 'GET')
    try:
        response = get(request_args['url'] + '/templates', headers=request_args['headers'])
    except exceptions.ConnectionError:
        raise IctvServerConnection(404)

    """ Raise IctvServerConnection if the server replies with status code different from 200 """
    if response.status_code != 200:
        raise IctvServerConnection(response.status_code)

    ictv_slides_templates = response.json()

    return {sub('^template-', '', i): ictv_slides_templates[i] for i in ictv_slides_templates
            if 'title-1' in ictv_slides_templates[i]}


def forge_link_url(chan, form):
    """
    Create the data structure to store the slide specific fields into the link_url entry in the Publishing
    :param chan: the channel from which come the slide data
    :param form: the actuel form from the Post
    :return: the data to store in the link_url entry of the Publishing
    """
    from re import sub
    link_post = ''
    slide_type = form.get(chan + '_slide-selector')
    if slide_type is not None:
        req = form.to_dict()
        for i in req:
            if chan + '_data_' + slide_type in i:
                a = sub('^' + chan + '_data_' + slide_type + '_', '', i)
                link_post += a + ":::" + req[i] + ','

        link_post += slide_type

    return link_post


def generate_ictv_dropdown_control(chan_name):
    """
    Generate the JS code to control the ictv slide dropdown from the Posts page
    :param chan_name: the name of the channel that requires the dropdown
    :return: the JS control code of the dropdown specific to the *chan_name* channel
    """
    code = 'function updateICTVForm(select) {' \
           '    var name = select.options[select.selectedIndex].value;' \
           '    $(".' + chan_name + '_ictv_slide_choice").hide();' \
                                    '    $("#' + chan_name + '_ictv_form_" + name).show();' \
                                                             '};'
    return code


def generate_ictv_dropdown(chan_name, templates):
    """
    Generate the ictv slide dropdown HTML code for the Posts page
    :param chan_name: the name of the channel that requires the dropdown
    :param templates: the list of the ictv templates proposed in the dropdown
    :return: the HTML code of the dropdown specific to the *chan_name* channel
    """
    ret = ''
    ret += '<div class="form-group">\n'
    ret += '\t<label for="' + chan_name + '_slide-selector">Slide type : </label><br>\n'
    ret += '\t<select id="' + chan_name + '_slide-selector" name="' + chan_name + '_slide-selector" class="form-control" onchange="updateICTVForm(this)">\n'
    for index, temp in enumerate(templates):
        ret += '\t\t<option value="' + temp + '">' + templates[temp]["description"] + '</option>\n'

    ret += '\t</select>\n'
    ret += '</div>\n'

    return ret


def generate_ictv_data_form(chan_name, templates):
    """
    Generate the ictv slide specific fields for each slide template given in templates
    :param chan_name: the name of the channel that requires the form
    :param templates: list of all the slide templates supported by both Superform and the ICTV server
    :return: the HTML code of the form
    """
    ret = ''

    for index, temp in enumerate(templates):
        div_id = chan_name + '_ictv_form_' + temp
        ret = ret + '<div id="' + div_id + '" class=\"' + chan_name + '_ictv_slide_choice\" ' + \
              ('style=\"display: none;\"' if index != 0 else '') + '>\n'
        ret = ret + '\t<h5>' + templates[temp]['name'] + '</h5>\n'

        for field in templates[temp]:
            if field != 'description' and field != 'name' and 'subtitle' not in field and 'title' not in field and \
                    'text' not in field:
                ret = ret + '\t<div class="form-group">\n'
                ret = ret + '\t\t<label for="' + chan_name + '_data_' + temp + '_' + field + \
                      '">' + field + '</label><br>\n'
                ret = ret + '\t\t<input type="text" name="' + chan_name + '_data_' + temp + '_' + field + \
                      '" id="' + chan_name + '_data_' + temp + '_' + field + '" class="form-control">\n'
                ret = ret + '\t</div>\n'

        ret = ret + '</div>\n'

    return ret


def generate_ictv_fields(chan_name, chan_config):
    """
    Generate a dict with all the ictv specific codr to inject into Posts page with Jijna
    :param chan_name: the name of the channel that requires the extended code
    :param chan_config: the configuration of the channel
    :return: the dict containing all the extendend code required in the Posts page
    """
    templates = get_ictv_templates(chan_name, chan_config)
    return {'dropdown': generate_ictv_dropdown(chan_name, templates),
            'data': generate_ictv_data_form(chan_name, templates),
            'control': generate_ictv_dropdown_control(chan_name),
            'error': ''}


def process_ictv_channels(channels):
    """
    Generate the fields to pass to the view form for each ictv channel
    :param channels: list of the ictv channels
    :return: the fields to pass to the view form
    """
    ret = {}
    for chan in channels:
        try:
            fields = generate_ictv_fields(chan.name, chan.config)
        except (IctvChannelConfiguration, IctvServerConnection) as e:
            ret[chan.name] = {'data': '', 'dropdown': '', 'control': '', 'error': e.popup()}
        else:
            ret[chan.name] = fields

    return ret


def generate_slide(chan_conf, pub):
    """
    Request the ICTV server the different slides layout and generate the slide corresponding to the publication data
    :param chan_conf: the configuration of the ictv channel
    :param pub: the publication to turn into a slide
    :return: the JSON representation of the slide
    :raise IctvServerConnection: if the communication with the server is impossible for any reason
    :raise IctvChannelConfiguration: if the channel is misconfigured and that does not allow to contact the ICTV server
    """
    splited_url = pub.link_url.split(',')

    """ Slide type is the last element of the list """
    slide_type = splited_url[-1]

    """ 
        Request the templates to the ICTV server 
        Raise IctvServerConnection, IctvChannelConfiguration
    """
    slides_templates = get_ictv_templates(str(pub.channel_id), chan_conf)
    if slide_type != '':
        slide_content = slides_templates[slide_type]
    else:
        raise IctvServerConnection(400, msg='slide')

    """ Copy extra data from ICTV specific form into the slide template """
    slide_data = {media_type: url for media_type, url in (media.split(':::') for media in splited_url[:-1])}
    for elem in slide_data:
        slide_content[elem] = {'src': slide_data[elem]}

        if 'background' in elem:
            slide_content[elem]['size'] = 'cover'

    """ Add publication data to the slide template """
    slide_content['title-1'] = {'text': pub.title}
    slide_content['text-1'] = {'text': pub.description}
    slide_content['subtitle-1'] = {'text': ''}
    slide_content.pop('name', None)
    slide_content.pop('description', None)

    return {'content': slide_content, 'template': 'template-' + slide_type, 'duration': -1}


def get_epoch(date):
    """
    Convert the given date into epoch format for ictv slide
    :param date: the date to convert
    :return: the epoch representation of the given date
    """
    return date.replace(tzinfo=datetime.timezone.utc).timestamp()


def generate_capsule(pub):
    """
    Create the JSON representation of the capsule that will contain the slide
    :param pub: the publication
    :return: the JSON capsule
    """
    capsule = {'name': pub.title + '-' + str(time()), 'theme': 'ictv', 'validity':
        [int(get_epoch(pub.date_from)), int(get_epoch(pub.date_until))]}
    return capsule


def run(pub, chan_conf):
    try:
        slide = generate_slide(chan_conf, pub)
    except (IctvServerConnection, IctvChannelConfiguration) as e:
        return StatusCode.ERROR, e.popup()

    capsule = generate_capsule(pub)

    """ Create new capsule on ICTV server on given channel """
    request_args = build_ictv_server_request_args(pub.channel_id, chan_conf, 'POST')
    capsules_url = request_args['url'] + '/capsules'
    capsule_request = post(capsules_url, json=capsule, headers=request_args['headers'])

    """ Check if the capsule has been created """
    if capsule_request.status_code == 201:
        capsule_id = capsule_request.headers['Location'].split('/')[-1]
        slide_url = capsules_url + '/' + str(capsule_id) + '/slides'
        slide_request = post(slide_url, json=slide, headers=request_args['headers'])
        if slide_request.status_code == 201:
            return StatusCode.OK, None
        else:
            return StatusCode.ERROR, IctvServerConnection(slide_request.status_code, msg='slide').popup()
    else:
        return StatusCode.ERROR, IctvServerConnection(capsule_request.status_code, msg='capsule').popup()
