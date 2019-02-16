import os
import tempfile
import pytest

from superform import app, db
from superform.models import Post, Publishing
from superform.utils import datetime_converter


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
            if login is not "myself":
                sess["admin"] = True
            else:
                sess["admin"] = False

            sess["logged_in"] = True
            sess["first_name"] = "gen_login"
            sess["name"] = "myname_gen"
            sess["email"] = "hello@genemail.com"
            sess['user_id'] = login


def test_delete_post(client):
    user_id = "myself"
    login(client, user_id)

    title_post = "title_test"
    descr_post = "description"
    link_post = "link"
    image_post = "img"
    date_from = datetime_converter("2018-01-01")
    date_until = datetime_converter("2018-01-10")
    p = Post(user_id=user_id, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()

    id_post = p.id

    path = '/delete_post/' + str(id_post)

    # verify that something has been posted/published
    assert db.session.query(Post).filter_by(id=id_post).first() is not None

    client.get(path)

    deleted_post = db.session.query(Post).filter_by(id=id_post).first()
    assert deleted_post is None


def test_delete_publishing(client):
    user_id = "myself"
    login(client, user_id)

    title_post = "title_test"
    descr_post = "description"
    link_post = "link"
    image_post = "img"
    date_from = datetime_converter("2018-01-01")
    date_until = datetime_converter("2018-01-10")
    p = Post(user_id=user_id, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()

    id_post = p.id
    id_channel = 1

    # Try with a publishing submitted for review (state=0)
    pub1 = Publishing(post_id=id_post, user_id=user_id, channel_id=id_channel, state=0, title=title_post, description=descr_post,
                      link_url=link_post, image_url=image_post, date_from=date_from, date_until=date_until)
    db.session.add(pub1)
    db.session.commit()

    path = '/delete_publishing/' + str(id_post) + '/' + str(id_channel)

    # verify that something has been posted/published
    assert db.session.query(Publishing).filter(Publishing.post_id == id_post).first() is not None

    client.get(path)

    deleted_publishing = db.session.query(Publishing).filter(Publishing.post_id == id_post).first()
    assert deleted_publishing is None

    # Try with a publishing already posted (state=1)
    pub2 = Publishing(post_id=id_post, channel_id=id_channel, state=1, title=title_post, description=descr_post,
                      link_url=link_post, image_url=image_post, date_from=date_from, date_until=date_until)
    db.session.add(pub2)
    db.session.commit()

    path = '/delete_publishing/' + str(id_post) + '/' + str(id_channel)

    # verify that something has been posted/published
    assert db.session.query(Publishing).filter(Publishing.post_id == id_post).first() is not None

    client.get(path)

    deleted_publishing = db.session.query(Publishing).filter(Publishing.post_id == id_post).first()
    assert deleted_publishing is None

    db.session.delete(p)
    db.session.commit()


# Not being able to delete someone else's post unless you're a moderator
def test_delete_not_author(client):
    user_id = "myself"
    user_id_author = "1"
    login(client, user_id)

    title_post = "title_test"
    descr_post = "description"
    link_post = "link"
    image_post = "img"
    date_from = datetime_converter("2018-01-01")
    date_until = datetime_converter("2018-01-10")
    p = Post(user_id=user_id_author, title=title_post, description=descr_post, link_url=link_post, image_url=image_post,
             date_from=date_from, date_until=date_until)
    db.session.add(p)
    db.session.commit()

    id_post = p.id

    path = '/delete/' + str(id_post)

    # verify that something has been posted/published
    assert db.session.query(Post).filter_by(id=id_post).first() is not None

    client.get(path)

    deleted_post = db.session.query(Post).filter_by(id=id_post).first()

    assert deleted_post is None

    db.session.delete(p)
    db.session.commit()
