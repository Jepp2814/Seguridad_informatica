 # Aporte de Vinicio Tipanguano

 # Aquí va mi contribución al laboratorio.
"""
Prueba de Vinicio Tipanguano: consulta concatenada vs. consulta parametrizada.
Usa una base SQLite en memoria, así que no crea ni modifica archivos del proyecto.
Ejecutar: python lab_sqli/prueba_vinicio.py
"""
import hashlib
import re
import sqlite3

# Solo letras, números y guion bajo, entre 3 y 20 caracteres.
PATRON_USUARIO = re.compile(r"^[a-zA-Z0-9_]{3,20}$")


def hash_clave(clave: str) -> str:
    # Solo para la demo. En una app real usa bcrypt, argon2 o pbkdf2 con sal.
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def crear_bd() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE usuarios (usuario TEXT PRIMARY KEY, clave_hash TEXT NOT NULL)"
    )
    conn.executemany(
        "INSERT INTO usuarios VALUES (?, ?)",
        [("admin", hash_clave("Admin123!")), ("vinicio", hash_clave("Unemi2026"))],
    )
    return conn


def login_inseguro(conn, usuario, clave) -> bool:
    # MAL: el texto del usuario se pega directamente en la consulta.
    consulta = (
        "SELECT usuario FROM usuarios "
        f"WHERE usuario = '{usuario}' AND clave_hash = '{hash_clave(clave)}'"
    )
    return conn.execute(consulta).fetchone() is not None


def login_seguro(conn, usuario, clave) -> bool:
    # BIEN: se valida la entrada y se usan parámetros (?).
    if not PATRON_USUARIO.match(usuario):
        return False
    fila = conn.execute(
        "SELECT usuario FROM usuarios WHERE usuario = ? AND clave_hash = ?",
        (usuario, hash_clave(clave)),
    ).fetchone()
    return fila is not None


def main():
    conn = crear_bd()
    casos = [
        ("Credenciales correctas", "vinicio", "Unemi2026"),
        ("Clave incorrecta", "vinicio", "otra"),
        ("Inyeccion SQL", "admin' --", "cualquiera"),
    ]
    print(f"{'Caso':<25}{'Inseguro':<12}{'Seguro':<12}")
    print("-" * 49)
    for nombre, usuario, clave in casos:
        inseguro = "ENTRA" if login_inseguro(conn, usuario, clave) else "bloqueado"
        seguro = "ENTRA" if login_seguro(conn, usuario, clave) else "bloqueado"
        print(f"{nombre:<25}{inseguro:<12}{seguro:<12}")
    conn.close()
    print("\nLa inyeccion entra en la version insegura y se bloquea en la segura.")


if __name__ == "__main__":
    main()