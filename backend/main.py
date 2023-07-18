from flask import Flask

app = Flask( __name__ )


texts = ["qweqwewq", "aseqwrwerwertf", "qweqwew123123"]

@app.route("/get_new_text")
def hello():
    print('front')
    global texts
    if len(texts) > 0:
        return texts.pop(0)
    return ""

app.run( host = "127.0.0.1", port = 5000 )