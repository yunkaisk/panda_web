from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db


bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username, abstract' 
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    )


    return render_template('blog/index.html',posts = posts)


@bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        abstract = request.form['abstract']
        error = None

        db = get_db()

        if title is None:
            error = "请输入标题"
        elif body is None:
            error = "请输入内容"

        if error is None:
            db.execute(
                'INSERT INTO post (title, body, author_id, abstract)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], abstract)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


@bp.route('/<int:id>/update', methods =('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        abstract = request.form['abstract']
        error = None

        if title is None:
            error = "请输入标题"
        elif body is None:
            error = "请输入内容"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?, abstract = ?'
                ' WHERE id = ?',
                (title, body, abstract, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

'''
删除post
'''

@bp.route('/<int:id>/delete', methods =('GET', 'POST'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


'''
post详情页面

'''
@bp.route('/p/<int:id>', methods = ('GET', 'POST'))
def post_body(id):
    post = get_post(id)
    return redirect(url_for('blog.p'), post = post)

'''
通过post.id来获取post
'''
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title,abstract, body, created, author_id,  username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} 不存在".format(id))

    # if check_author and post['author_id'] != g.user['id']:
    #     abort(403)

    return post


