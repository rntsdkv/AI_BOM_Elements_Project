import datetime

from flask import Flask, render_template, jsonify, request, make_response, Response, send_file
from functions import *
from item import Item
import string
import secrets
import sql
from result import Result

alphabet = string.ascii_letters + string.digits + '_'

app = Flask(__name__)


def check_folders():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    if not os.path.exists("uploads"):
        os.makedirs("uploads")


@app.route("/")
def index():
    user_id = ''.join(secrets.choice(alphabet) for i in range(20))
    response = make_response(render_template('index.html'))
    response.set_cookie("user_id", user_id)
    return response

results = {"Магниторезистентный цифровой вольтметр": [Item("Конструктор прибор, вольтметр+амперметр цифровой, SVAL0013PW", "https://www.chipdip.ru/product0/8031325911", image="https://static.chipdip.ru/lib/304/DOC045304074.jpg")],
           "Миллиомметр": [Item("DT-5302, Миллиомметр", "https://www.chipdip.ru/product/dt-5302", image="https://static.chipdip.ru/lib/249/DOC005249889.jpg")]}


@app.route("/search")
def search():
    user_id = request.cookies.get("user_id")
    if not user_id:
        return render_template('not_cookie.html')
    return render_template('search.html', titles=[], results=[], length=0)
    # return render_template('search.html', titles=list(results), results=results, length=len(results))
    # items = get_chipdip(query)
    # return render_template('search.html', len=len(items), Items=items)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Нет файла"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({'error': 'Файл не выбран'}), 400

    check_folders()
    file_path = os.path.join("downloads", request.cookies.get("user_id") + '.' + file.filename.split('.')[-1])
    file.save(file_path)

    return jsonify({"message": "Файл успешно загружен", "filename": file.filename})


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.form.to_dict()
    print(data)
    message_id = sql.add_message(datetime.datetime.now(), data['user_id'], data['text'])
    llm_invoke(message_id, data['text'])
    if message_id:
        return jsonify({"id": message_id, "status_code": 200})
    return jsonify({"status_code": 400})


@app.route('/get_message_answer', methods=['GET'])
def get_message_answer():
    try:
        user_id = request.args.get("user_id")
        message_id = request.args.get("message_id")
    except:
        return Response(status=500)
    answer = sql.get_message_answer(user_id, message_id)

    if answer is None:
        return jsonify({"has_answer": "false"})
    return jsonify({"has_answer": "true", "text": answer})


# results = {"Магниторезистентный цифровой вольтметр": [],
#            "Миллиомметр": []}

@app.route('/get_result', methods=['GET'])
def get_result():
    print("НОВЫЙ ЗАПРОС")

    user_id = request.args.get("user_id")
    file = find_file(user_id)
    result = Result().from_list(search_BOM(file)).as_list()
    print(result)
    return jsonify({"result": result})


@app.route('/regenerate', methods=['GET'])
def regenerate():
    user_id = request.args.get("user_id")
    selected_item_id = int(request.args.get("selected_item_id"))
    text = request.args.get("text")
    result: Result = sql.get_items(user_id)
    new_item = re_search(result.list_of_items[selected_item_id-1], text)[1]
    result = result.replace_item(selected_item_id - 1, new_item)
    sql.set_items(user_id, result)
    return jsonify({"result": result})


@app.route("/downloads")
def downloads():
    return render_template('downloads.html')


@app.route("/install")
def install():
    user_id = request.args.get("user_id")
    result: Result = sql.get_items(user_id)
    result.generate_report(user_id)
    return send_file("uploads/" + user_id + ".xlsx", as_attachment=True)


if __name__ == "__main__":
    check_folders()
    sql.create_items_table()
    sql.create_messages_table()
    app.run(host="localhost", port=3550, debug=True)
