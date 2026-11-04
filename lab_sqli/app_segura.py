import os
import sqlite3
from contextlib import closing

from flask import Flask, request, render_template_string
from werkzeug.security import check_password_hash, generate_password_hash

DB = "seguro.db"
P = 5001
M_L = 100

app = Flask(__name__)

PAGINA = """
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{{ titulo }}</title>
<style>
body{font-family: sans-serif;max-width: 720px;margin: 30px auto}
input{margin:4px 0;padding:6px}
table{border-collapse:collapse;margin-top:10px}
td, th{border:1px solid #999;padding:4px 10px}
.err{color:#b00}.ok{color:#080}
</style>
</head>
<body>
<h2>{{ titulo }}</h2>

<h3>Login</h3>
<form method="post" action="/login">
    <input name="username" placeholder="usuario"><br>
    <input name="password" type="password" placeholder="contraseña"><br>
    <button>Ingresar</button>
</form>

<h3>Buscar productos</h3>
<form method="get" action="/buscar">
    <input name="q" placeholder="nombre del producto"><br>
    <button>Buscar</button>
</form>
<hr>

{% if mensaje %}<p class="{{ clase }}">{{ mensaje }}</p>{% endif %}

{% if rows is not none %}
<table>
    <tr><th>ID</th><th>nombre</th><th>precio</th></tr>
    {% for row in rows %}
    <tr class="fila"><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td></tr>
    {% endfor %}
</table>
{% endif %}
</body>
</html>
"""
def conectar():
    return sqlite3.connect(DB)

def init_db(db=DB, hashed=False):
    """Crea la BD de demostración. hashed=True guarda contraseñas con hash."""
    if os.path.exists(db):
        os.remove(db)

    with closing(sqlite3.connect(db)) as con:
        con.executescript("""
            CREATE TABLE users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
            CREATE TABLE products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL
            );
        """)

        usuarios = [
            ("admin", "admin123", "administrador"),
            ("yamel", "yamel2026", "usuario"),
            ("jose", "jose95", "usuario"),
        ]
        for u, p, r in usuarios:
            con.execute(
                "INSERT INTO users(username, password, role) VALUES (?, ?, ?)",
                (u, generate_password_hash(p) if hashed else p, r),
            )

        productos = [("Laptop", 850.0), ("Mouse", 15.5), ("Teclado", 30.0),
                     ("Monitor", 210.0), ("Auricular", 45.0)]
        con.executemany(
            "INSERT INTO products(nombre, precio) VALUES (?, ?)", productos
        )
        con.commit()

def render(**kw):
    datos = dict(titulo="Tienda Segura(DEMO)", mensaje=None, clase="", rows=None)
    datos.update(kw)
    return render_template_string(PAGINA, **datos)

@app.route("/")
def index():
    return render()

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")[:M_L]
    password = request.form.get("password", "")[:M_L]

    try:
        with closing(conectar()) as con:
            fila = con.execute(
                "SELECT id, username, role, password FROM users "
                "WHERE username = ?",
                (username,),
            ).fetchone()
    except sqlite3.Error:
        app.logger.exception("Error al consultar la base de datos")
        return render(mensaje="Error al intentar iniciar sesión", clase="err"), 500

    if fila and check_password_hash(fila[3], password):
        return render(mensaje=f"Bienvenido {fila[1]} (rol: {fila[2]})", clase="ok")
    return render(mensaje="Usuario o contraseña incorrectos", clase="err"), 401

@app.route("/buscar")
def buscar():
    q = request.args.get("q", "")[:M_L]

    try:
        with closing(conectar()) as con:
            rows = con.execute(
                "SELECT id, nombre, precio FROM products WHERE nombre LIKE ?",
                (f"%{q}%",),
            ).fetchall()
    except sqlite3.Error:
        app.logger.exception("Error al consultar la base de datos")
        return render(mensaje="Error al intentar buscar productos", clase="err"), 500

    return render(rows=rows)

if __name__ == "__main__":
    init_db(hashed=True)
    app.run(host="127.0.0.1", port=P, debug=False)