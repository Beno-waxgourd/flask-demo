from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import psycopg2.extras
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.tables import Users,Post

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    # db = get_db()
    # cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # cursor.execute(
    #     """SELECT p.id, title, body, created, author_id, username
    #     FROM post AS p JOIN users AS u ON p.author_id = u.id
    #     ORDER BY created DESC"""
    # )
    # posts = cursor.fetchall()

    #
    # 1
    #

    db = get_db()
    posts = db.execute(
        """SELECT p.id, title, body, created, author_id, username
        FROM post AS p JOIN users AS u ON p.author_id = u.id
        ORDER BY created DESC"""
    ).fetchall()
    # print(posts)

    #
    # 2
    #

    # p, u = db.query(Post, Users.username).filter(Post.author_id == Users.id).order_by(Post.created).all()[0]
    # posts = [(p.id, p.title, p.body, p.created, p.author_id, u)]
    # print(posts)

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
            # cursor = db.cursor()
            # insert_query = """ INSERT INTO post (title, body, author_id) VALUES (%s, %s, %s) """
            # item_tuple = (title, body, g.users['id'])
            # cursor.execute(insert_query, item_tuple)
            new_post = Post(title = title, body = body, author_id = g.users['id'])
            db.add(new_post)
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    db = get_db()
    # cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # cursor.execute("""SELECT p.id, title, body, created, author_id, username FROM post p JOIN users u ON p.author_id = u.id WHERE p.id = %d""" %(id) )
    # post = cursor.fetchone()
    # post = db.execute("""SELECT p.id, title, body, created, author_id, username FROM post p JOIN users u ON p.author_id = u.id WHERE p.id = %d""" %(id) ).fetchone()
    post = db.query(Post, Users.username).filter(Post.id == id).outerjoin(Users, Users.id == Post.author_id).first()
    p, u = post
    print(p, u)
    print(p.id, p.title, p.body, p.author_id, p.created, u)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and p.author_id != g.users['id']:
        abort(403)
    # abort() 会引发一个特殊的异常，返回一个 HTTP 状态码。
    # 404 表示“未找到”， 403 代表“禁止访问”。
    return p

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    p = get_post(id)

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
            # cursor = db.cursor()
            # update_query = """ UPDATE post SET title = %s, body = %s WHERE id = %s """
            # item_tuple = (title, body, id)
            # cursor.execute(update_query, item_tuple)
            # db.execute(""" UPDATE post SET title = %s, body = %s WHERE id = %s """, (title, body, id))
            db.query(Post).filter(Post.id == id).update({Post.title:title, Post.body:body})
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=p)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    # cursor = db.cursor()
    # cursor.execute("DELETE FROM post WHERE id = %d" %(id))
    # db.execute("DELETE FROM post WHERE id = %d" %(id))
    db.query(Post).filter(Post.id == id).delete()
    db.commit()
    return redirect(url_for('blog.index'))