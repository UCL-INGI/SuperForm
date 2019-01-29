import datetime
import os
import tempfile

import pytest

from superform import app, db
from superform.plugins import mail


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
    
    
def test_run_mail(client):
    #Is there a way to test a send mail function?
    assert True == True
