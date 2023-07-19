#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask
import argparse
import logging
import sys

from Translator import Translator
from Config import Config

app = Flask(__name__)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger()


@app.route("/get_new_text")
def hello():
    log.info('thread front')
    return app.config['translator'].getText()


def getParameters():
    parser = argparse.ArgumentParser(
        prog='Clipboard Transate',
        description='Get screenshot from clipboard and translates it.')

    parser.add_argument('-c', '--config-path', default='config.ini')
    args = parser.parse_args()
    config = Config(args.config_path)

    log.info('running with: {}'.format(config.to_dict()))
    return config


def main():
    config = getParameters()
    app.config['translator'] = Translator(log, config)
    app.run(host=config.host, port=config.port, debug=True, use_reloader=False)
    app.config['translator'].stop()


if __name__ == '__main__':
    main()
