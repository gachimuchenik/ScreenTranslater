#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask
import argparse
import logging

from Translator import Translator

app = Flask(__name__)
log = logging.Logger('main')


@app.route("/get_new_text")
def hello():
    log.info('thread front')
    return app.config['translator'].getText()


def getParameters():
    parser = argparse.ArgumentParser(
        prog='Clipboard Transate',
        description='Get screenshot from clipboard and translates it.')
    parser.add_argument('-p', '--tesseract_path',
                        default='C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=5000)
    parser.add_argument('--x1', default=250)
    parser.add_argument('--y1', default=770)
    parser.add_argument('--x2', default=1600)
    parser.add_argument('--y2', default=1000)
    args = parser.parse_args()
    log.info('running with: tesseract_path={},\nhost={}\nport={}'.format(
        args.tesseract_path, args.host, args.port))
    return args


def main():
    args = getParameters()
    translator = Translator(log, args)

    app.config['translator'] = translator
    app.run(host=args.host, port=args.port, debug=True, threaded=True)

    translator.stop()


if __name__ == '__main__':
    main()
