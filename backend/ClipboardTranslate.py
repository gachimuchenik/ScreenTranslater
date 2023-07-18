#!/usr/bin/python3

from flask import Flask
import argparse

from Translator import Translator

app = Flask(__name__)


@app.route("/get_new_text")
def hello():
    print('thread front', flush=True)
    global texts
    if len(texts) > 0:
        return texts.pop(0)
    return ""


def getParameters():
    parser = argparse.ArgumentParser(
        prog='Clipboard Transate',
        description='Get screenshot from clipboard and translates it.')
    parser.add_argument('-p', '--tesseract_path',
                        default='C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=5000)
    args = parser.parse_args()
    return args


def main():
    args = getParameters()
    translator = Translator(args.tesseract_path)

    app.run(host=args.host, port=args.port, debug=True, threaded=True)
    translator.stop()


if __name__ == '__main__':
    main()
