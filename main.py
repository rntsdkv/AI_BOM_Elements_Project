from flask import Flask, render_template
from functions import *

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/search/<query>")
def search(query=None):
    items = get_chipdip(query)
    return render_template('search.html', len=len(items), Items=items)


@app.route("/download_example")
def download_example():
    return render_template('downloads.html')


if __name__ == "__main__":
    app.run(host="localhost", port=3550)
