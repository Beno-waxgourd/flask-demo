import os
# import db

from flask import Flask
from flaskr import auth
from flaskr import blog


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    # from . import auth
    app.register_blueprint(auth.bp)
    # 使用 app.register_blueprint() 导入并注册蓝图

    # from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    # 我们使用 app.add_url_rule() 关联端点名称 'index' 和 / URL ，这样 url_for('index') 或 url_for('blog.index') 都会有效，会生成同样的 / URL 。

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()