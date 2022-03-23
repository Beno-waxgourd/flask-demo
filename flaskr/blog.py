from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import psycopg2.extras
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute(
        """SELECT p.id, title, body, created, author_id, username 
        FROM post AS p JOIN users AS u ON p.author_id = u.id 
        ORDER BY created DESC"""
    )
    posts = cursor.fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            insert_query = """ INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s) """
            item_tuple = (title, body, g.users['id'])
            cursor.execute(insert_query, item_tuple)

            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("""SELECT p.id, title, body, created, author_id, username FROM post p JOIN users u ON p.author_id = u.id WHERE p.id = %d""" %(id) )
    post = cursor.fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.users['id']:
        abort(403)
    # abort() 会引发一个特殊的异常，返回一个 HTTP 状态码。
    # 404 表示“未找到”， 403 代表“禁止访问”。
    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            update_query = """ UPDATE post SET title = %s, body = %s WHERE id = %s """
            item_tuple = (title, body, id)
            cursor.execute(update_query, item_tuple)
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM post WHERE id = %d" %(id))
    db.commit()
    return redirect(url_for('blog.index'))