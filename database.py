import sqlite3

def create_db():
    conn = sqlite3.connect("intellihire.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()


# ✅ REGISTER (FIXED)
def register_user(email, password):
    if not email or not password:
        return "❌ Email & Password required"

    conn = sqlite3.connect("intellihire.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        return "❌ User already exists"

    c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()

    return "✅ Registered successfully"


# ✅ LOGIN (FIXED)
def login_user(email, password):
    if not email or not password:
        return False

    conn = sqlite3.connect("intellihire.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    data = c.fetchone()

    conn.close()

    return True if data else False


def save_result(email, result):
    conn = sqlite3.connect("intellihire.db")
    c = conn.cursor()

    c.execute("INSERT INTO results (email, result) VALUES (?, ?)", (email, result))
    conn.commit()
    conn.close()


def get_history(email):
    conn = sqlite3.connect("intellihire.db")
    c = conn.cursor()

    c.execute("SELECT result FROM results WHERE email=?", (email,))
    data = c.fetchall()

    conn.close()

    return "\n\n".join([r[0] for r in data])