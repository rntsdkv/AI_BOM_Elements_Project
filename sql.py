import datetime
import pickle
import sqlite3
from result import Result
from item import Item


def create_messages_table():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime NOT NULL,
        user_id VARCHAR(20) NOT NULL,
        text STRING NOT NULL,
        answer STRING
    );
    """)
    con.commit()
    con.close()


def create_items_table():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        user_id VARCHAR(20) NOT NULL UNIQUE,
        result STRING NOT NULL
    );
    """)
    con.commit()
    con.close()


def add_message(datetime, user_id, text):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    id = cur.execute("""
    INSERT INTO messages (datetime, user_id, text)
    VALUES (?, ?, ?);
    """, (datetime, user_id, text)).lastrowid
    con.commit()
    con.close()
    return id


def add_message_answer(message_id, text):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("""
    UPDATE messages
    SET answer = ?
    WHERE id = ?;
    """, (text, message_id))
    con.commit()
    con.close()


def get_message_answer(user_id, message_id):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    result = cur.execute("""
    SELECT answer
    FROM messages
    WHERE user_id = ? AND id = ?;
    """, (user_id, message_id)).fetchone()
    con.close()

    if result:
        return result[0]

    return None


def set_items(user_id: str, result: Result):
    pickled = pickle.dumps(result)
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("""
    REPLACE INTO items (user_id, result)
    VALUES (?, ?);
    """, (user_id, pickled))
    con.commit()
    con.close()


def get_items(user_id: str):
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    result = cur.execute("""
    SELECT result
    FROM items
    WHERE user_id = ?;
    """, (user_id,)).fetchone()
    con.close()

    if result:
        result = pickle.loads(result[0])
        return result

    return None


if __name__ == "__main__":
    # create_messages_table()
    # # print(add_message(datetime.datetime.now(), "test", "message"))
    # add_message_answer(1, "go sex")
    create_items_table()
    # set_items("test", Result().from_list(list_of_items=[("SEX", Item("pex", "shneks", 1))]))
    print(get_items("test"))