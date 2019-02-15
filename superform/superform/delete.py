from flask import Blueprint, url_for, redirect, session, render_template, flash

from superform.utils import login_required
from superform.models import db, Post, Publishing, User, Channel
from superform.users import is_moderator

from superform.run_plugin_exception import RunPluginException

import json

delete_page = Blueprint('delete', __name__)


@delete_page.route('/delete/<int:id>', methods=['GET'])
@login_required()
def delete(id):
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None
    drafts = []
    unmoderated = []
    posted = []

    has_draft = False
    has_unmoderated = False
    has_posted = False

    if user is not None:
        setattr(user, 'is_mod', is_moderator(user))
        post = db.session.query(Post).filter_by(id=id).first()
        if post is not None:
            post_user_id = post.user_id
            if post_user_id == user.id or user.is_mod:
                publishings = db.session.query(Publishing).filter(Publishing.post_id == id).all()
                for pub in publishings:
                    # The publishing is a draft
                    if pub.state == -1:
                        drafts.append(pub)
                        has_draft = True

                    # The publishing has been submitted for review
                    elif pub.state == 0:
                        unmoderated.append(pub)
                        has_unmoderated = True

                    # The publishing has been posted
                    elif pub.state == 1:

                        channel = db.session.query(Channel).filter(Channel.id == pub.channel_id).first()
                        # The channel is Facebook
                        if channel.module == "superform.plugins.facebook":
                            posted.append((pub, "fb"))
                            has_posted = True
                        # The channel is Wiki
                        elif channel.module == "superform.plugins.wiki":
                            posted.append((pub, "wiki"))
                            has_posted = True
                        else:
                            posted.append((pub, "0"))
                            has_posted = True

                    # The publishing has been archived
                    else:
                        pass
            else:
                # The user trying to delete the post is not the one who created it
                flash("You don't have the rights to delete this post (not the creator)")
        else:
            # The post does not exist
            return render_template('404.html'), 404
    else:
        # User is not connected
        return render_template('403.html'), 403

    if has_draft or has_unmoderated or has_posted:
        return render_template("delete.html", user=user, post=post, draft_pubs=drafts,
                               unmoderated_pubs=unmoderated, posted_pubs=posted, has_draft=has_draft,
                               has_unmoderated=has_unmoderated, has_posted=has_posted)
    else:
        return delete_post(id)


@delete_page.route('/delete_post/<int:id>', methods=['GET', 'POST'])
@login_required()
def delete_post(id):
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None

    if user is not None:
        setattr(user, 'is_mod', is_moderator(user))
        post = db.session.query(Post).filter_by(id=id).first()
        if post is not None:
            post_user_id = post.user_id
            if post_user_id == user.id or user.is_mod:
                publishings = db.session.query(Publishing).filter(Publishing.post_id == id).all()
                post_del_cond = True
                for _ in publishings:
                    # If there is any publishing
                    post_del_cond = False

                # If every publishing linked to the post has been deleted (otherwise violation of constraint in db)
                if post_del_cond:
                    db.session.delete(post)
                    db.session.commit()
                else:
                    flash("At least one publishing remains, cannot delete post")
            else:
                # The user trying to delete the post is not the one who created it
                flash("You don't have the rights to delete this post (not the creator)")
        else:
            # The post does not exist
            return render_template('404.html'), 404
    else:
        # User is not connected
        return render_template('403.html'), 403

    return redirect(url_for('index'))


@delete_page.route('/delete_publishing/<int:post_id>/<int:channel_id>', methods=['GET', 'POST'])
@login_required()
def delete_publishing(post_id, channel_id):
    user = User.query.get(session.get("user_id", "")) if session.get("logged_in", False) else None

    if user is not None:
        setattr(user, 'is_mod', is_moderator(user))
        post = db.session.query(Post).filter_by(id=post_id).first()
        if post is not None:
            post_user_id = post.user_id
            if post_user_id == user.id or user.is_mod:
                publishings = db.session.query(Publishing).filter(Publishing.post_id == post_id).all()
                channel = db.session.query(Channel).filter(Channel.id == channel_id).first()
                for pub in publishings:
                    if pub.channel_id == channel.id:
                        # The publishing has been posted
                        if pub.state == 1:
                            flash("The publishing has been posted")
                            return redirect(url_for('delete.delete', id=post_id))

            else:
                # The user is trying to delete the publishing linked to a post he did not create
                flash("You don't have the rights to delete this post (not the creator)")
        else:
            # The post does not exist
            return render_template('404.html'), 404
    else:
        # User is not connected
        return render_template('403.html'), 403

    return redirect(url_for('delete.delete', id=post_id))
