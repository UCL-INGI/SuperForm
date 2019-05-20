import json
import os
import tempfile

import pytest

from superform import app, db, Post
from superform.models import Post, Channel, Publishing, Authorization
from superform.utils import get_module_full_name


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture
def client():
    app.app_context().push()
    db_fd, database = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + database + ".db"
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    clear_data(db.session)
    os.close(db_fd)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///superform.db"


def login(client, login):
    with client as c:
        with c.session_transaction() as sess:
            if login is not "myself":
                sess["admin"] = True
            else:
                sess["admin"] = False

            sess["logged_in"] = True
            sess["first_name"] = "gen_login"
            sess["name"] = "myname_gen"
            sess["email"] = "hello@genemail.com"
            sess['user_id'] = login


## Testing Functions ##


def test_edit_access(client):
    login(client, "myself")
    rv = client.post('/new', data=dict(titlepost='A new test post', descriptionpost="A description",
                                       linkurlpost="http://www.test.com", imagepost="image.jpg",
                                       datefrompost="2018-07-01", dateuntilpost="2018-07-01"))
    assert rv.status_code == 302
    posts = db.session.query(Post).all()
    assert len(posts) > 0
    last_add = posts[-1]
    url = '/edit/' + str(last_add.id)
    rv = client.get(url)
    assert rv.status_code == 200
    db.session.query(Post).filter(Post.id == last_add.id).delete()
    db.session.commit()


def test_edit_new_post(client):
    login(client, "myself")
    rv = client.post('/new', data=dict(titlepost='A new test post', descriptionpost="A description",
                                       linkurlpost="http://www.test.com", imagepost="image.jpg",
                                       datefrompost="2018-07-01", dateuntilpost="2018-07-01"))
    assert rv.status_code == 302
    posts = db.session.query(Post).all()
    last_add = posts[-1]
    url = '/edit/publish_edit_post/' + str(last_add.id)
    dictionary = {"name": "General", "fields": dict(title='An edited test post', description="A description",
                                                    linkurl="http://www.test.com", image="image.jpg",
                                                    datefrom="2018-07-01",
                                                    dateuntil="2018-07-01")}
    rv = client.post(url, data=json.dumps([dictionary]))
    assert rv.status_code == 200
    edited_posts = db.session.query(Post).all()
    assert len(posts) == len(edited_posts)
    edited_post = edited_posts[-1]
    assert edited_post.title == 'An edited test post'
    assert last_add.id == edited_post.id
    assert edited_post.description == "A description"
    db.session.query(Post).filter(Post.id == last_add.id).delete()
    db.session.commit()


def test_edit_forbidden(client):
    login(client, "myself")
    rv = client.post('/new', data=dict(titlepost='A new test post', descriptionpost="A description",
                                       linkurlpost="http://www.test.com", imagepost="image.jpg",
                                       datefrompost="2018-07-01", dateuntilpost="2018-07-01"))
    assert rv.status_code == 302
    posts = db.session.query(Post).all()
    last_add = posts[-1]
    url_get = '/edit/' + str(last_add.id)
    url_post = '/edit/publish_edit_post/' + str(last_add.id)
    login(client, "alterego")
    rv = client.get(url_get)
    assert rv.status_code == 200
    dictionary = {"name": "General", "fields": dict(title='An edited test post', description="A description",
                                                    linkurl="http://www.test.com", image="image.jpg",
                                                    datefrom="2018-07-01", dateuntil="2018-07-01")}
    rv = client.post(url_post, data=json.dumps([dictionary]))
    assert rv.status_code == 403
    edited_posts = db.session.query(Post).all()
    assert len(posts) == len(edited_posts)
    edited_post = edited_posts[-1]
    assert edited_post.title == 'A new test post'
    assert last_add.id == edited_post.id
    assert edited_post.description == "A description"
    db.session.query(Post).filter(Post.id == last_add.id).delete()
    db.session.commit()


def test_edit_new_publishing(client):
    login(client, "myself")
    channel = Channel(id=0, name="test", module=get_module_full_name("mail"), config="{}")
    db.session.add(channel)
    a = Authorization(channel_id=channel.id, user_id="myself", permission=1)
    db.session.add(a)
    db.session.commit()
    datadict = dict(titlepost='A new test post', descriptionpost="A description", linkurlpost="http://www.test.com",
                    imagepost="image.jpg", datefrompost="2018-07-01", dateuntilpost="2018-07-01")
    datadict[str(channel.name) + '_titlepost'] = "mail title"
    datadict[str(channel.name) + '_descriptionpost'] = 'mail description'
    datadict[str(channel.name) + '_linkurlpost'] = "http://www.test.com"
    datadict[str(channel.name) + '_imagepost'] = "image.jpg"
    datadict[str(channel.name) + '_datefrompost'] = "2018-07-01"
    datadict[str(channel.name) + '_dateuntilpost'] = "2018-07-01"
    rv = client.post('/new', data=datadict)
    assert rv.status_code == 302
    posts = db.session.query(Post).all()
    last_add = posts[-1]
    url = '/edit/publish_edit_post/' + str(last_add.id)
    datadict2 = dict(title='An edited test post', description="A description",
                     link_url="http://www.test.com",
                     image="image.jpg", date_from="2018-07-01", date_until="2018-07-01")
    datadict3 = dict(title='mail title', description='edited mail description', date_from="2018-07-01",
                     date_until="2018-07-01")
    rv = client.post(url,
                     data=json.dumps([{"name": "General", "fields": datadict2}, {"name": "test", "fields": datadict3}]))
    assert rv.status_code == 200
    edited_posts = db.session.query(Post).all()
    assert len(posts) == len(edited_posts)
    edited_post = edited_posts[-1]
    assert edited_post.title == 'An edited test post'
    assert last_add.id == edited_post.id
    assert edited_post.description == "A description"
    edited_publishing = db.session.query(Publishing).filter(Publishing.post_id == last_add.id)
    assert edited_publishing[0].title == "mail title"
    assert edited_publishing[0].description == "edited mail description"
    # cleaning up
    db.session.query(Post).filter(Post.id == last_add.id).delete()
    db.session.query(Publishing).filter(Publishing.post_id == last_add.id).delete()
    db.session.delete(a)
    db.session.delete(channel)
    db.session.commit()
