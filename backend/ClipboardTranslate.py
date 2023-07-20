#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os

from flask import Flask

from lib.image_getter import ImageGetter
from lib.image_translater import ImageTranslater
from lib.processor import Processor
from lib.config import Config
from lib.utils import make_logger

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
    log = make_logger(config)
    log.info('==========Started==========\nparams={}'.format(config.to_dict()))

    app.config['translator'] = Processor(
        log, config, ImageGetter(config.use_fake_image_getter), ImageTranslater(log, config))
    app.run(host=config.host, port=config.port, debug=True, use_reloader=False)
    app.config['translator'].stop()


if __name__ == '__main__':
    main()
