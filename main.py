from flask import Flask, render_template
from functions import *
from item import Item

app = Flask(__name__)

results = {"Магниторезистентный цифровой вольтметр": [Item("https://www.chipdip.ru/product0/8031325911", "Конструктор прибор, вольтметр+амперметр цифровой, SVAL0013PW", image="https://static.chipdip.ru/lib/304/DOC045304074.jpg")],
           "Миллиомметр": [Item("https://www.chipdip.ru/product/dt-5302", "DT-5302, Миллиомметр", image="https://static.chipdip.ru/lib/249/DOC005249889.jpg")]}


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/search/<query>")
def search(query=None):
    items = get_chipdip(query)
    return render_template('search.html', len=len(items), Items=items)


@app.route("/downloads")
def downloads():
    return render_template('downloads.html')


if __name__ == "__main__":
    app.run(host="localhost", port=3550)
