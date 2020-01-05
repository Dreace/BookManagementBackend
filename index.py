import gevent.monkey

from scheduler import scheduler

gevent.monkey.patch_all()
import plugin
from pywsgi import WSGIServer
from os import path
import coloredlogs
from flask import Flask
from flask import Response
# from werkzeug.contrib.fixers import ProxyFix
from flask_cors import CORS
import flask_compress
import json
import traceback
from flask import request
from logging.config import dictConfig
import logging
from redis_connect import redis_session
import load_task

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': "[%(asctime)s %(filename)s %(funcName)s %(lineno)d] %(levelname)s %(message)s",
    }},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': 'log/flask.log',
            'encoding': 'utf8',
            'when': 'midnight',
            # 'maxBytes': 8 * 1024 * 1000,
            'backupCount': 7,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
})

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
flask_compress.Compress(app)


@app.errorhandler(Exception)
def on_sever_error(e):
    message = "服务器错误"
    code = -1
    data = ""
    logging.error(traceback.format_exc())
    resp = Response(json.dumps({"message": message, "code": code, "data": data}),
                    mimetype='application/json')
    return resp


no_auth_required_url = ["Login", "GetBookList", "Logout"]


# @app.before_request
def check_auth():
    message = "无权限"
    code = -10
    data = ""
    cookies_session = request.cookies.get("session", "")
    session = redis_session.get(cookies_session)
    if request.path[1:] not in no_auth_required_url and not session:
        resp = Response(json.dumps({"message": message, "code": code, "data": data}),
                        mimetype='application/json')
        return resp
    else:
        redis_session.expire(cookies_session, 86400)


def initializer(context=None):
    root_logger = logging.getLogger("root")
    coloredlogs.DEFAULT_LEVEL_STYLES = dict(spam=dict(color='green', faint=True),
                                            debug=dict(color='green'),
                                            verbose=dict(color='blue'),
                                            info=dict(color='white'),
                                            notice=dict(color='magenta'),
                                            warning=dict(color='yellow'),
                                            success=dict(color='green', bold=True),
                                            error=dict(color='red'),
                                            critical=dict(color='red', bold=True))
    coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
                                        'hostname': {'color': 'magenta'},
                                        'levelname': {'color': 'black', 'bold': True},
                                        'name': {'color': 'blue'},
                                        'filename': {'color': 'green'},
                                        'funcName': {'color': 'green'},
                                        'lineno': {'color': 'green'},
                                        'programname': {'color': 'cyan'}}
    coloredlogs.install(fmt="[%(asctime)s %(filename)s %(funcName)s %(lineno)d] %(levelname)s %(message)s",
                        level='INFO', logger=root_logger)
    plugins = plugin.load_plugins(
        path.join(path.dirname(__file__), 'plugins'),
        'plugins'
    )
    for i in plugins:
        app.register_blueprint(i.api)
    load_task.load_tasks(
        path.join(path.dirname(__file__), 'tasks'),
        'tasks')
    scheduler.start()


if __name__ == '__main__':
    initializer()
    root_logger = logging.getLogger("root")
    http_server = WSGIServer(('0.0.0.0', 105), app, log=root_logger, error_log=root_logger)
    http_server.serve_forever()


def handler(environ, start_response):
    return app(environ, start_response)
