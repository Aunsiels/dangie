import logging
import os
from logging.config import fileConfig

from flask import Flask, request
from flask.logging import create_logger

from dangie.config import Config
from dangie.homepage.blueprint import BP as BP_HOMEPAGE


def get_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr


def create_app(testing=False):
    if not testing:
        if not os.path.exists('logs'):
            os.makedirs('logs')
        fileConfig(os.path.abspath(os.path.dirname(__file__)) +
                   '/logging.cfg')
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["TESTING"] = testing
    app.register_blueprint(BP_HOMEPAGE)
    logger = create_logger(app)
    if testing:
        logger.setLevel(logging.DEBUG)

    @app.before_request
    # pylint: disable=unused-variable
    def log_the_request():
        if not app.config["TESTING"]:
            logger.info("\t".join([get_ip(),
                                   request.url,
                                   str(request.data)
                                   ]))

    return app
