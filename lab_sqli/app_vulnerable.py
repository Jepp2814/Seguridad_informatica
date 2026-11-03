import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, render_template_string, request

DB = Path(__file__).resolve().parent.parent / "vulnerable.db"
PUERTO = 5000
app = Flask(__name__)

PAGINA = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tienda Vulnerable (DEMO)</title>
    <style>
        body {
            font-family: sans-serif;
            max-width: 720px;
            margin: 30px auto;
            padding: 0 16px;
        }
        input {
            margin: 4px 0;
            padding: 6px;
        }
        table {
            border-collapse: collapse;
            margin-top: 10px;
        }
        td, th {
            border: 1px solid #999;
            padding: 4px 10px;
        }
        .err { color: #b00; }
        .ok { color: #080; }
        pre {
            background: #eee;
            padding: 12px;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }
    </style>
</head>
<body>
    <h2>Tienda Vulnerable (DEMO)</h2>
    <p>Laboratorio educativo: aplicación intencionalmente vulnerable.</p>
    <h3>Login</h3>
    <form method="post" action="/login">
        <input name="username" placeholder="usuario"><br>
        <input name="password" type="password"
               placeholder="contraseña"><br>
        <button type="submit">Ingresar</button>
    </form>
    <h3>Buscar productos</h3>
    <form method="get" action="/buscar">
        <input name="q" placeholder="nombre del producto"
               value="{{ q }}"><br>
        <button type="submit">Buscar</button>
    </form>
    <hr>
    {% if mensaje %}
        <p class="{{ clase }}">{{ mensaje }}</p>
    {% endif %}
    {% if query %}
        <h3>Consulta ejecutada</h3>
        <pre>{{ query }}</pre>
    {% endif %}
    {% if rows is not none %}
        <table>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Precio / dato</th>
            </tr>
            {% for row in rows %}
                <tr class="fila">
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td>{{ row[2] }}</td>
                </tr>
            {% endfor %}
        </table>
        {% if not rows %}
            <p>No se encontraron resultados.</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""

def conectar():
    return sqlite3.connect(DB, timeout=5)

def init_db():
    with closing(conectar()) as con:
        with con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL
                )
            """)
            usuarios = [
                ("admin", "admin123", "administrador"),
                ("yamel", "yamel2026", "usuario"),
                ("jose", "jose95", "usuario"),
            ]
            con.executemany(
                """
                INSERT OR IGNORE INTO users (username, password, role)
                VALUES (?, ?, ?)
                """,
                usuarios,
            )
            cantidad = con.execute(
                "SELECT COUNT(*) FROM products"
            ).fetchone()[0]

            if cantidad == 0:
                productos = [
                    ("Laptop", 850.0),
                    ("Mouse", 15.5),
                    ("Teclado", 30.0),
                    ("Monitor", 210.0),
                    ("Auricular", 45.0),
                ]
                con.executemany(
                    "INSERT INTO products (nombre, precio) VALUES (?, ?)", productos,)

def render(**kwargs):
    datos = {
        "mensaje": None,
        "clase": "",
        "query": None,
        "rows": None,
        "q": "",
    }
    datos.update(kwargs)
    return render_template_string(PAGINA, **datos)

@app.route("/")
def index():
    return render()

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")[:100]
    password = request.form.get("password", "")[:100]
    query = (
        "SELECT id, username, role FROM users "
        "WHERE username = ? AND password = ?"
    )
    try:
        with closing(conectar()) as con:
            fila = con.execute(query, (username, password)).fetchone()
    except sqlite3.Error as error:
        return render(
            mensaje=f"Error SQL: {error}", clase="err", query=query,), 500
    if fila:
        return render(
            mensaje=f"Bienvenido, {fila[1]} (rol: {fila[2]})",
            clase="ok",
            query=query,)
    return render(
        mensaje="Credenciales inválidas",
        clase="err",
        query=query,), 401

@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")[:100]
    query = (
        "SELECT id, nombre, precio FROM products "
        "WHERE nombre LIKE ?"
    )
    try:
        with closing(conectar()) as con:
            rows = con.execute(query, (f"%{q}%",)).fetchall()
    except sqlite3.Error as error:
        return render(
            mensaje=f"Error SQL: {error}",
            clase="err",
            query=query,
            q=q,), 500
    return render(rows=rows, query=query, q=q)

def main():
    parser = argparse.ArgumentParser(
        description="Laboratorio local de SQL Injection.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Elimina vulnerable.db y recrea los datos ficticios.",)
    args = parser.parse_args()
    if args.reset and DB.exists():
        DB.unlink()
    init_db()
    app.run(host="127.0.0.1", port=PUERTO, debug=False)

if __name__ == "__main__":
    main()