import os
import sqlite3
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create DB if not exists
conn = sqlite3.connect('chat.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER,
    role TEXT,
    content TEXT,
    FOREIGN KEY(thread_id) REFERENCES threads(id)
)''')
conn.commit()

@app.route("/threads", methods=["GET", "POST"])
def threads():
    if request.method == "POST":
        name = request.json.get("name", "New Chat")
        c.execute("INSERT INTO threads (name) VALUES (?)", (name,))
        conn.commit()
        return jsonify({"id": c.lastrowid, "name": name})
    else:
        c.execute("SELECT * FROM threads")
        return jsonify([{"id": row[0], "name": row[1]} for row in c.fetchall()])

@app.route("/messages/<int:thread_id>", methods=["GET", "POST"])
def messages(thread_id):
    if request.method == "POST":
        role = request.json.get("role")
        content = request.json.get("content")
        c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, role, content))
        conn.commit()
        return jsonify({"id": c.lastrowid, "role": role, "content": content})
    else:
        c.execute("SELECT role, content FROM messages WHERE thread_id=?", (thread_id,))
        return jsonify([{"role": row[0], "content": row[1]} for row in c.fetchall()])

@app.route("/chat/<int:thread_id>", methods=["POST"])
def chat(thread_id):
    c.execute("SELECT role, content FROM messages WHERE thread_id=?", (thread_id,))
    msgs = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    user_msg = request.json.get("message")
    msgs.append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        temperature=0.7,
        max_tokens=500
    )

    reply = response.choices[0].message.content
    c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, "user", user_msg))
    c.execute("INSERT INTO messages (thread_id, role, content) VALUES (?, ?, ?)", (thread_id, "assistant", reply))
    conn.commit()

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)