import functools
import psycopg2
import psycopg2.extras
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
# 这里创建了一个名称为 'auth' 的Blueprint。
# 和应用对象一样，蓝图需要知道是在哪里定义的，因此把 __name__ 作为函数的第二个参数。 url_prefix会添加到所有与该蓝图关联的URL前面。

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # request.form 是一个特殊类型的 dict ，其映射了提交表单的键和值。
        db = get_db()
        cursor = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                insert_query = """ INSERT INTO users (username, password) VALUES (%s, %s) """
                # item_tuple = (username, generate_password_hash(password))
                item_tuple = (username, generate_password_hash(password))
                cursor.execute(insert_query, item_tuple)
                # 使用 generate_password_hash() 生成安全的哈希值，再把哈希值储存到数据库中
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
                # 如果用户名已存在，会产生一个IntegrityError错误，应当将该错误作为一个验证错误显示给用户。
            else:
                return redirect(url_for("auth.login"))
                # redirect()为生成的 URL 生成一个重定向响应。

        flash(error)
        # 如果验证失败，那么会向用户显示一个出错信息。 flash() 用于储存在渲染模块时可以调用的信息。

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        error = None
        # select_query = """ SELECT * from users WHERE username= %s AND password= %s """
        # item_tuple = (username, password)
        # cursor.execute(select_query,item_tuple)
        cursor.execute(""" SELECT * from users WHERE username= %s """, (username,))
        users = cursor.fetchone()

        # print(users,db,cursor)
        # print(cursor.execute(select_query, item_tuple))
        # print(cursor.fetchone())

        # posts = cursor.fetchall()
        # print("posts:",posts)
        # cursor.execute(
        #     'SELECT * FROM users WHERE username = ?', (username,))
        # user = cursor.fetchone()
        # fetchone() 根据查询返回一个记录行。如果查询没有结果，则返回 None。

        if users is None:
            error = 'Incorrect username or password.'
        elif not check_password_hash(users['password'], password):
            # check_password_hash() 以相同的方式哈希提交的 密码并安全的比较哈希值。如果匹配成功，那么密码就是正确的。
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            # session是一个 dict, 它用于储存横跨请求的值。当验证成功后，用户的 id 被储存于一个新的会话中。
            # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。
            session["user_id"] = users['id']
            session["username"] = users['username']
            # session['user_id'] = users['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.users = None
    else:
        db = get_db()
        cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("""SELECT * FROM users WHERE id = %s""", (user_id,))
        res = cursor.fetchone()
        g.users = {"id": res[0], "username": res[1]}

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.users is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view