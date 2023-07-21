#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import logging

from flask import Flask

from lib.config import Config
from lib.utils import make_logger, make_image_processor

app = Flask(__name__)
log = None


@app.route("/get_new_text")
def hello():
    log.info('thread front')
    return app.config['translator'].get_processed_data()


def getParameters():
    parser = argparse.ArgumentParser(
        prog='Clipboard Transate',
        description='Get screenshot from clipboard and translates it.')

    parser.add_argument('-c', '--config-path', default='config.ini')
    args = parser.parse_args()
    config = Config(os.path.dirname(__file__), args.config_path)
    return config


def main():
    config = getParameters()
    make_logger(config)
    log = logging.getLogger("main")
    log.info('==========Started==========\nparams={}'.format(config.to_dict()))

    app.config['translator'] = make_image_processor(config)
    app.run(host=config.host, port=config.port, debug=True, use_reloader=False)
    app.config['translator'].stop()


if __name__ == '__main__':
    main()
