# To run : Be sure to be in Superform/superform folder and then 'pytest -v' in your terminal
import datetime
import os
import tempfile

import pytest

from superform.models import Authorization, Channel
from superform import app, db, Post, Publishing, User


chan_id_3 = -1  # Should be created
chan_id_4 = -1  # Shouldn't be created

@pytest.fixture
def client():
    app.app_context().push()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def login(client, login):
    with client as c:
        with c.session_transaction() as sess:
            if login is "myself":
                sess["admin"] = True
            else:
                sess["admin"] = False

            sess["logged_in"] = True
            sess["first_name"] = "gen_login"
            sess["name"] = "myname_gen"
            sess["email"] = "hello@genemail.com"
            sess['user_id'] = login


## Testing Functions ##

def test_new_channel_as_admin(client):
    global chan_id_3, chan_id_4
    login(client, "myself")

    # Create a test channel
    client.post("/channels", data={'@action': 'new', 'name': 'test_channel_ictv_1', 'module': 'ictv'})
    chan = db.session.query(Channel).all()[-1]
    assert chan
    chan_id_3 = chan.id
    assert chan_id_3 >= 0

    # Configure the channel
    ictv_server_fqdn = '0.0.0.0:8000'
    ictv_channel_id = '1'
    ictv_api_key = 'azertyuiop'
    client.post("/configure/" + str(chan_id_3), data={"ictv_server_fqdn": ictv_server_fqdn,
                                                      "ictv_channel_id": ictv_channel_id,
                                                      "ictv_api_key": ictv_api_key})
    chan = db.session.query(Channel).filter(Channel.id == chan_id_3).first()
    assert chan

    # Check channel configuration
    chan_creds = chan.config
    assert chan_creds == "{\"ictv_server_fqdn\" : \"" + ictv_server_fqdn\
        + "\",\"ictv_channel_id\" : \"" + ictv_channel_id \
        + "\",\"ictv_api_key\" : \"" + ictv_api_key + "\"}"

def test_new_channel_no_admin(client):
    global chan_id_3, chan_id_4
    login(client, "alterego")

    # Create a test channel
    client.post("/channels", data={'@action': 'new', 'name': 'test_channel_ictv_2', 'module': 'ictv'})
    chan = db.session.query(Channel).all()[-1]
    assert chan
    chan_id_4 = chan.id
    assert chan_id_4 == chan_id_3
    chan_id_4 = -1

    # Configure the channel
    client.post("/configure/" + str(chan_id_4), data={"ictv_server_fqdn": '0.0.0.0:8000',
                                                      "ictv_channel_id": '1',
                                                      "ictv_api_key": 'azertyuiop'})
    chan = db.session.query(Channel).filter(Channel.id == chan_id_4).first()
    assert not chan

def test_new_publish_ictv(client):
    global chan_id_3, chan_id_4
    login(client, "myself")

    chan = db.session.query(Channel).filter(Channel.id == chan_id_3).first()
    assert chan

    title = 'A test new ictv post'
    description = 'Some random content, just what we need for a test'
    image = 'image.jpg'
    # Create a post
    d = datetime.date.today()
    d += datetime.timedelta(1)
    client.post('/new', data=dict(titlepost=title, descriptionpost=description,
                                  imagepost = image,
                                  datefrompost=d.strftime("%Y-%m-%d"),
                                  timefrompost=d.strftime("%H:%M"),
                                  dateuntilpost=d.strftime("%Y-%m-%d"),
                                  timeuntilpost=d.strftime("%H:%M")))
    post = db.session.query(Post).filter(Post.title == title) \
        .filter(Post.description == description).all()[-1]
    assert post
    assert title == post.title

    # Publish a post
    client.post('/publish',
                data={'chan_option_' + str(chan.id): "chan_option_0", 'titlepost': title,
                      'descriptionpost': description,
                      'imagepost': image,
                      'datefrompost': d.strftime("%Y-%m-%d"),
                      'timefrompost': d.strftime("%H:%M"),
                      'dateuntilpost': d.strftime("%Y-%m-%d"),
                      'timeuntilpost': d.strftime("%H:%M")})
    pub = db.session.query(Publishing).filter(Publishing.title == title) \
        .filter(Publishing.description == description).all()[-1]
    assert pub
    assert title == pub.title

    # Moderate a post
    print(chan_id_3)
    print(chan.id)
    client.post('/moderate/' + str(pub.post_id) + '/' + str(chan.id), data={'titlepost': title,
                                                           'descrpost': description,
                                                           'imagepost': image,
                                  'datefrompost': d.strftime("%Y-%m-%d"),
                                  'timefrompost': d.strftime("%H:%M"),
                                  'dateuntilpost': d.strftime("%Y-%m-%d"),
                                  'timeuntilpost': d.strftime("%H:%M")})

    # Cleaning up
    db.session.delete(post)
    db.session.delete(pub)
    db.session.commit()

def test_delete_channel_no_admin(client):
    global chan_id_3, chan_id_4
    login(client, "alterego")

    client.post("/channels", data={'@action': 'delete', 'id': chan_id_3})

    chan = db.session.query(Channel).filter(Channel.id == chan_id_3).first()
    assert chan

def test_delete_channel_as_admin(client):
    global chan_id_3, chan_id_4
    login(client, "myself")

    client.post("/channels", data={'@action': 'delete', 'id': chan_id_3})

    chan = db.session.query(Channel).filter(Channel.id == chan_id_3).first()
    assert not chan










