import importlib
import pkgutil

from flask import Flask, render_template, session, request

import superform.plugins
from superform.authentication import authentication_page
from superform.authorizations import authorizations_page
from superform.edit import edit_page
from superform.stats import stats_page
from superform.channels import channels_page
from superform.delete import delete_page
from superform.models import db, User, Post, Publishing, Channel, State, Comment
from superform.posts import posts_page
from superform.search import search_page
from superform.publishings import pub_page
from superform.users import get_moderate_channels_for_user, is_moderator
from superform.plugins.pdf import export
from superform.plugins._rss_page import rss_page
from superform.plugins._linkedin_callback import linkedin_page
from superform.plugins._facebook_callback import facebook_page

app = Flask(__name__)
app.config.from_json("config.json")

# Register blueprints
app.register_blueprint(authentication_page)
app.register_blueprint(authorizations_page)
app.register_blueprint(channels_page)
app.register_blueprint(delete_page)
app.register_blueprint(edit_page)
app.register_blueprint(facebook_page)
app.register_blueprint(linkedin_page)
app.register_blueprint(posts_page)
app.register_blueprint(pub_page)
app.register_blueprint(rss_page)
app.register_blueprint(search_page)
app.register_blueprint(stats_page)

# Init dbs
db.init_app(app)

# List available channels in config
# TEAM 7 Fb/Linkedin
app.config["PLUGINS"] = {}
for finder, name, ispkg in pkgutil.iter_modules(superform.plugins.__path__, superform.plugins.__name__ + "."):
    if name[18] != '_':  # do not include files starting with an underscore (useful for callback pages)
        app.config["PLUGINS"][name] = importlib.import_module(name)
# TEAM 7 Fb/Linkedin

# TEAM 8 Moderation
SIZE_COMMENT = 40


# TEAM 8 Moderation


@app.route('/', methods=['GET', 'POST'])
def index():
    # Team06: Export to PDF feature
    if request.method == "POST":
        action = request.form.get('@action', '')
        if action == "export":
            post_id = request.form.get("id")
            chan_id = request.form.get("template")
            return export(post_id, chan_id)
    # end addition

    user_id = session.get("user_id", "") if session.get("logged_in", False) else -1
    user = User.query.get(user_id) if session.get("logged_in", False) else None

    # TEAM06: add – pdf
    pdf_chans = db.session.query(Channel).filter(
        Channel.module == 'superform.plugins.pdf'
    )
    # end add
    posts_var = []
    pubs_unvalidated = []
    chans = []

    if user is not None and user_id != -1:
        setattr(user, 'is_mod', is_moderator(user))
        chans = get_moderate_channels_for_user(user)

        # AJOUTER Post.user_id == user_id dans posts DANS QUERY?
        posts_var = db.session.query(Post).filter(Post.user_id == user_id).order_by(Post.date_created.desc())
        for post in posts_var:
            publishings_var = db.session.query(Publishing).filter(Publishing.post_id == post.id).all()
            channels_var = set()
            for publishing in publishings_var:
                channels_var.add(db.session.query(Channel).filter(Channel.id == publishing.channel_id).first())
            setattr(post, "channels", channels_var)

        posts_user = db.session.query(Post).filter(Post.user_id == user_id).all()
        pubs_unvalidated = db.session.query(Publishing).filter(Publishing.state == State.REFUSED.value). \
            order_by(Publishing.post_id).order_by(Publishing.channel_id).all()
        post_ids = [p.id for p in posts_user]

        for pub_unvalidated in pubs_unvalidated:
            if pub_unvalidated.post_id in post_ids:
                channels_var = [db.session.query(Channel).filter(Channel.id == pub_unvalidated.channel_id).first()]
                setattr(pub_unvalidated, "channels", channels_var)
                last_comment = db.session.query(Comment).filter(Comment.publishing_id ==
                                                                pub_unvalidated.publishing_id).first()
                comm = comm_short = last_comment.moderator_comment[:SIZE_COMMENT]
                if len(last_comment.moderator_comment) > SIZE_COMMENT:
                    comm_short = comm + "..."

                comm = last_comment.moderator_comment
                setattr(pub_unvalidated, "comment_short", comm_short)
                setattr(pub_unvalidated, "comment", comm)
    # TEAM06: changes in the render_template, templates
    return render_template("index.html", posts=posts_var, pubs_unvalidated=pubs_unvalidated,
                           templates=pdf_chans, user=user, channels=chans)


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


@app.errorhandler(404)
def notfound(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # To use Flask over HTTPS we need to generate a certificate (cert.pem) and a key (key.pem)
    # and pass this option to Flask : --cert cert.pem --key key.pem
    app.run(ssl_context='adhoc')
