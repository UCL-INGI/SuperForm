import os
import pytest
import tempfile

from superform.models import Authorization
from superform import app, db
from tests.test_basic import create_user, create_channel


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture
def client():
    app.app_context().push()

    db_fd, database = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+database+".db"
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


# Testing Functions #


def test_logged_but_not_moderator(client):
    create_user(id="myself", name="myself", first_name="utilisateursearch",
                email="utilisateursearch.test@uclouvain.be")
    create_channel("test_search", "mail", {'sender': 'noOne', 'receiver': 'noOne'})

    login(client, "myself")
    rv2 = client.get('/', follow_redirects=True)
    assert rv2.status_code == 200
    assert "You are not logged in." not in rv2.data.decode()

    filter = {}
    filter["subject"] = " "
    filter["sorted"] = "id"
    filter["body"] = " "
    r = client.post("http://127.0.0.1:5000/search_post", data=filter)
    assert r.status_code == 200


def test_not_moderator(client):
    create_user(id="test", name="test", first_name="utilisateur", email="utilisateur.test@uclouvain.be")
    create_channel("test_search", "mail", {'sender': 'noOne', 'receiver': 'noOne'})

    login(client, "test")

    r = client.post("http://127.0.0.1:5000/search_publishings", data={
        "subject": "",
        "body": "",
        "author": "",
        "channels": "test"
    })

    assert r.status_code == 200  # 403?


def test_search_unlogged_client_publishing_search(client):
    create_user(id="test", name="test", first_name="utilisateur", email="utilisateur.test@uclouvain.be")
    create_channel("test_search", "mail", {'sender': 'noOne', 'receiver': 'noOne'})
    a = Authorization(channel_id=1, user_id="test", permission=2)
    db.session.add(a)

    r = client.post("http://127.0.0.1:5000/search_publishings", data={
        "subject": "",
        "body": "",
        "author": "",
        "channels": "test"
    })

    assert r.status_code == 403


def test_search_unlogged_client_post_search(client):
    create_user(id="test", name="test", first_name="utilisateur", email="utilisateur.test@uclouvain.be")
    create_channel("test_search", "mail", {'sender': 'noOne', 'receiver': 'noOne'})
    a = Authorization(channel_id=1, user_id="test", permission=2)
    db.session.add(a)

    r = client.post("http://127.0.0.1:5000/search_post", data={
        "subject": "",
        "body": "",
        "sorted": ""
    })

    assert r.status_code == 403  # 200
    # assert len(r.text) == 2
    # assert r.text == "[]"


def test_search_publishing_valid_client(client):
    create_user(id="test", name="test", first_name="utilisateur", email="utilisateur.test@uclouvain.be")
    create_channel("test_search", "mail", {'sender': 'noOne', 'receiver': 'noOne'})
    a = Authorization(channel_id=1, user_id="test", permission=2)
    db.session.add(a)

    login(client, "test")

    r = client.post("http://127.0.0.1:5000/search_publishings", data={
        "subject": "",
        "body": "",
        "author": "",
        "channels": "test"
    })

    assert r.status_code == 200  # 403


def test_search_post_valid_login(client):
    create_user(id="myself", name="myself", first_name="utilisateursearch",
                email="utilisateursearch.test@uclouvain.be")
    create_channel("test_search", "mail", {'sender': 'noOne', 'receiver': 'noOne'})

    login(client, "myself")

    r = client.post("http://127.0.0.1:5000/search_post", data={
        "subject": "",
        "body": "",
        "sorted": ""
    })

    assert int(r.status_code) == 200
