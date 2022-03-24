import os
import sys
import psycopg2
import click
from flask import current_app, g
# g 是一个特殊对象，独立于每一个请求。
# 在处理请求过程中，它可以用于储存可能多个函数都会用到的数据。
# 把连接储存于其中，可以多次使用，而不用在同一个 请求中每次调用 get_db 时都创建一个新的连接。
from flask.cli import with_appcontext

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# def get_db():
#     if 'db' not in g:
#         conn = psycopg2.connect(database="flask_demo", user='postgres', password='password', host='127.0.0.1', port='5432')
#         # print('connect successful')
#         g.db = conn
#     return g.db

def get_db():
    if 'db' not in g:
        engine = create_engine('postgresql+psycopg2://postgres:password@127.0.0.1:5432/flask_demo')
        # print('connect successful')
        g.db = scoped_session(sessionmaker(bind=engine))
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():

    db = get_db()
    # cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        # open_resource() 打开一个文件，该文件名是相对于flaskr包的。
        # print('open success')
        # print(f.readline().decode('utf8'))
        """
        db.to_sql(f.read().decode('utf8'))
        db.executescript(f.read().decode('utf8'))
        """
        # cursor.execute(f.read().decode('utf8'))
        db.execute(f.read().decode('utf8'))
    db.commit()
    print('exec success')


@click.command('init-db')
# click.command() 定义一个名为init-db命令行，它调用init_db函数，并为用户显示一个成功的消息。
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    # app.teardown_appcontext() 告诉Flask在返回响应后进行清理的时候调用此函数。
    app.cli.add_command(init_db_command)
    # app.cli.add_command() 添加一个新的可以与flask一起工作的命令。

# if __name__ == '__main__':
#
#     # connectPostgreSQL()
#
#     conn = psycopg2.connect(database="flask_demo", user='postgres', password='password', host='127.0.0.1', port='5432')
#     print('connect successful')
#     cursor = conn.cursor()
#     cursor.execute('''DROP TABLE IF EXISTS users;
# DROP TABLE IF EXISTS post;
#
# CREATE TABLE users (
#   id SERIAL PRIMARY KEY,
#   username TEXT UNIQUE NOT NULL,
#   password TEXT NOT NULL
# );
#
# CREATE TABLE post (
#   id SERIAL PRIMARY KEY,
#   author_id INTEGER NOT NULL,
#   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
#   title TEXT NOT NULL,
#   body TEXT NOT NULL,
#   FOREIGN KEY (author_id) REFERENCES users (id)
# );''')
#     print('Table created successfully')
#     conn.commit()
#     conn.close()



