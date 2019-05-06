from flask import session, render_template, Blueprint
from sqlalchemy import desc

from superform.users import is_moderator
from superform.models import User, db, Post, Publishing, Channel, State, Authorization, Permission
from superform.utils import login_required

lists_page = Blueprint('lists', __name__)


def get_publications(user):
    if user is None:
        return []
    setattr(user, 'is_mod', is_moderator(user))
    my_pubs = []
    if user is not None:
        my_pubs = [pub for _, _, pub in db.session.query(Channel, Post, Publishing)
            .filter(Channel.id == Publishing.channel_id)
            .filter(Publishing.post_id == Post.id)
            .filter(Post.user_id == user.id).order_by(desc(Publishing.post_id))]
    return my_pubs


def get_publications_to_moderate(user):
    moderable_pubs_per_chan = [pub for _, _, pub in db.session.query(Authorization, Channel, Publishing)
        .filter(Authorization.user_id == user.id, Authorization.permission == Permission.MODERATOR.value)
        .filter(Authorization.channel_id == Publishing.channel_id)
        .filter(Publishing.post_id == Post.id).filter(Channel.id == Publishing.channel_id)
        .filter(Publishing.state == State.NOTVALIDATED.value)
        .order_by(desc(Publishing.post_id)).all()]
    return moderable_pubs_per_chan


@lists_page.route('/my_refused_publishings', methods=['GET'])
@login_required()
def refused_publishings():
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None
    return render_template("lists.html", title="Refused publishings", user=user, my_publishings=get_publications(user),
                           state=State.REFUSED.value, states=State)


@lists_page.route('/my_accepted_publishings', methods=['GET'])
@login_required()
def accepted_publishings():
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None
    return render_template("lists.html", title="Accepted publishings", user=user, my_publishings=get_publications(user),
                           state=State.VALIDATED.value, states=State)


@lists_page.route('/my_unmoderated_publishings', methods=['GET'])
@login_required()
def unmoderated_publishings():
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None
    return render_template("lists.html", title="Unmoderated publishings", user=user,
                           my_publishings=get_publications(user), state=State.NOT_VALIDATED.value, states=State)
