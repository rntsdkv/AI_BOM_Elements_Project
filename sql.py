import datetime
import sqlite3


def create_messages_table():
    con = sqlite3.connect("data.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime NOT NULL,
        user_id VARCHAR(20) NOT NULL,
        text STRING NOT NULL,
        answer
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


if __name__ == "__main__":
    create_messages_table()
    # print(add_message(datetime.datetime.now(), "test", "message"))
    add_message_answer(1, "go sex")
    print(get_last_message_answer("test"))