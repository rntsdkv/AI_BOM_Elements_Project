from flask import Flask, render_template, jsonify, request, make_response
from functions import *
from item import Item
import string
import secrets

alphabet = string.ascii_letters + string.digits + '_'

app = Flask(__name__)

results = {"Магниторезистентный цифровой вольтметр": [Item("Конструктор прибор, вольтметр+амперметр цифровой, SVAL0013PW", "https://www.chipdip.ru/product0/8031325911", image="https://static.chipdip.ru/lib/304/DOC045304074.jpg")],
           "Миллиомметр": [Item("DT-5302, Миллиомметр", "https://www.chipdip.ru/product/dt-5302", image="https://static.chipdip.ru/lib/249/DOC005249889.jpg")]}

print(results)


def check_downloads():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")


@app.route("/")
def index():
    user_id = ''.join(secrets.choice(alphabet) for i in range(20))
    response = make_response(render_template('index.html'))
    response.set_cookie("user_id", user_id)
    return response


@app.route("/search")
def search():
    user_id = request.cookies.get("user_id")
    if not user_id:
        return render_template('not_cookie.html')
    return render_template('search.html', titles=list(results), results=results, length=len(results))
    # items = get_chipdip(query)
    # return render_template('search.html', len=len(items), Items=items)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Нет файла"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({'error': 'Файл не выбран'}), 400

    print(request.cookies.get("user_id"))
    print(file.filename)

    check_downloads()
    file_path = os.path.join("downloads", request.cookies.get("user_id") + '.' + file.filename.split('.')[-1])
    file.save(file_path)

    return jsonify({"message": "Файл успешно загружен", "filename": file.filename})


@app.route("/downloads")
def downloads():
    return render_template('downloads.html')


if __name__ == "__main__":
    check_downloads()
    app.run(host="localhost", port=3550, debug=True)
