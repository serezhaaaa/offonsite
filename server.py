import socket
import time
import sqlite3
from datetime import datetime
from flask import Flask, render_template_string

app = Flask(__name__)

ARDUINO_IP = "192.168.0.84"
ARDUINO_PORT = 8888

DB_NAME = "logs.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_log(action):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO logs (action, timestamp) VALUES (?, ?)",
        (action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()


def send_udp(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (ARDUINO_IP, ARDUINO_PORT))
        sock.close()
        time.sleep(0.3)

        print(f"[УСПЕХ] Отправлен пакет '{message}' на {ARDUINO_IP}:{ARDUINO_PORT}")

    except Exception as e:
        print(f"[ОШИБКА] Не удалось отправить UDP: {e}")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Arduino UDP Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background-color: #f4f4f9;
            padding-top: 50px;
        }

        h1 {
            color: #333;
        }

        .btn {
            display: inline-block;
            width: 150px;
            padding: 20px;
            margin: 10px;
            font-size: 20px;
            font-weight: bold;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            transition: 0.2s;
        }

        .btn-on {
            background-color: #2ec4b6;
        }

        .btn-on:hover {
            background-color: #25a195;
        }

        .btn-off {
            background-color: #e71d36;
        }

        .btn-off:hover {
            background-color: #c0182d;
        }

        iframe {
            display: none;
        }

        table {
            margin: 30px auto;
            border-collapse: collapse;
        }

        th, td {
            border: 1px solid #ccc;
            padding: 8px 15px;
        }
    </style>
</head>
<body>

<h1>Управление Arduino по UDP</h1>

<a href="/action/on" target="hidden-form" class="btn btn-on">ON (F)</a>
<a href="/action/off" target="hidden-form" class="btn btn-off">OFF (G)</a>

<br><br>

<a href="/logs" target="_blank">Открыть журнал действий</a>

<iframe name="hidden-form"></iframe>

</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/action/on")
def action_on():
    send_udp("F")
    save_log("ON")
    return "OK"


@app.route("/action/off")
def action_off():
    send_udp("G")
    save_log("OFF")
    return "OK"


@app.route("/logs")
def logs():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT id, action, timestamp FROM logs ORDER BY id DESC"
    )

    rows = cur.fetchall()
    conn.close()

    html = """
    <h1>Журнал действий</h1>

    <table>
        <tr>
            <th>ID</th>
            <th>Действие</th>
            <th>Время</th>
        </tr>
    """

    for row in rows:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
        </tr>
        """

    html += "</table>"

    return html


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5050, debug=True)